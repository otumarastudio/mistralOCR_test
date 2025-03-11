import os
import base64
import re
from datetime import datetime
from pathlib import Path
from mistralai import Mistral
import dotenv

dotenv.load_dotenv()  # .env 파일에서 환경 변수를 불러옵니다.


# 디버깅 출력 여부 (True로 설정 시 모든 디버깅 메시지 출력)
DEBUG = False

def setup_client():
    """Mistral 클라이언트 초기화"""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY가 설정되지 않았습니다.")
    return Mistral(api_key=api_key)

def upload_pdf(client, pdf_path):
    """PDF 파일 업로드 및 사인드 URL 반환"""
    with open(pdf_path, "rb") as pdf_file:
        uploaded_file = client.files.upload(
            file={"file_name": os.path.basename(pdf_path), "content": pdf_file},
            purpose="ocr"
        )
    return client.files.get_signed_url(file_id=uploaded_file.id).url

def process_ocr(client, signed_url):
    """OCR 처리 실행"""
    return client.ocr.process(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": signed_url},
        include_image_base64=True
    )

def save_image(img_obj, img_dir, page_num, img_num):
    """이미지 저장 및 파일명 반환"""
    try:
        img_base64 = img_obj.image_base64.split("base64,")[-1]
        img_bytes = base64.b64decode(img_base64)
        img_filename = f"page_{page_num}_img_{img_num}.jpeg"
        img_path = img_dir / img_filename
        with open(img_path, "wb") as img_file:
            img_file.write(img_bytes)
        if DEBUG:
            print(f"  페이지 {page_num}, 이미지 {img_num} 출력:")
            display(Image(data=img_bytes))
        return img_filename
    except Exception as e:
        print(f"  이미지 처리 실패 (page {page_num}, img {img_num}): {e}")
        return None

def process_page(page, page_num, img_dir, f):
    """페이지 처리 및 Markdown 작성"""
    markdown_text = page.markdown
    if DEBUG:
        print(f"\nPage {page_num} Markdown (원본):")
        print(markdown_text)

    image_count = 0
    if hasattr(page, "images") and page.images:
        if DEBUG:
            print(f"Page {page_num} 이미지 처리:")
        for j, img_obj in enumerate(page.images):
            if DEBUG:
                print(f"  이미지 {j}: {img_obj}")
            if hasattr(img_obj, "image_base64") and img_obj.image_base64:
                img_filename = save_image(img_obj, img_dir, page_num, j + 1)
                if img_filename:
                    img_id = img_obj.id
                    pattern = rf"!\[{img_id}\]\({img_id}\)"
                    replacement = f"![Image {j + 1}](./images/{img_filename})"
                    markdown_text = re.sub(pattern, replacement, markdown_text)
                    image_count += 1
            elif DEBUG:
                print(f"  페이지 {page_num}, 이미지 {j + 1}: base64 데이터 없음")
    elif DEBUG:
        print(f"Page {page_num}: 인식된 이미지가 없습니다.")

    f.write(f"# Page {page_num}\n\n")
    f.write(markdown_text + "\n\n")
    if DEBUG:
        print(f"Page {page_num} Markdown (수정됨):")
        print(markdown_text)
    
    return image_count

def main():
    # PDF 경로
    pdf_path = "data/2305.03393v1-pg9.pdf" # 실제 PDF 파일 경로로 변경
    pdf_name = Path(pdf_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("result") / f"{pdf_name}_{timestamp}"
    img_dir = output_dir / "images"
    output_path = output_dir / f"{pdf_name}.md"

    # 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(exist_ok=True)

    # 클라이언트 및 OCR 처리
    client = setup_client()
    signed_url = upload_pdf(client, pdf_path)
    ocr_response = process_ocr(client, signed_url)

    # 페이지별 이미지 개수 출력
    if DEBUG:
        print("페이지별 이미지 개수:")
        for i in range(len(ocr_response.pages)):
            print(f"Page {i}: {len(ocr_response.pages[i].images)}")

    # 결과 처리
    total_images = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for i, page in enumerate(ocr_response.pages):
            total_images += process_page(page, i + 1, img_dir, f)

    # 결과 출력
    print(f"\nOCR 결과가 {output_path}에 저장되었습니다.")
    if total_images > 0:
        print(f"{total_images}개의 이미지가 {img_dir}에 저장되고 Markdown에 반영되었습니다.")
    else:
        print("추출된 이미지가 없습니다.")

if __name__ == "__main__":
    main()