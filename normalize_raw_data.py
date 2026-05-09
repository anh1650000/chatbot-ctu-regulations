"""
*******File này em nhờ AI tạo giúp chuẩn hóa dữ liệu thô nhanh ạ**********
Script để chuẩn hóa tất cả file .txt trong thư mục raw_data/:
- Xóa dấu cách thừa (nhiều space thành 1 space)
- Xóa dòng trống
- Ghi đè file đã chuẩn hóa
"""

import os
import re
from pathlib import Path

def normalize_text_file(file_path: Path) -> tuple[int, int]:
    """
    Chuẩn hóa một file text:
    - Xóa khoảng trắng thừa
    - Xóa dòng trống
    
    Returns:
        (số dòng trước, số dòng sau)
    """
    print(f"📄 Đang xử lý: {file_path.name}")
    
    try:
        # Đọc file với encoding utf-8
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_line_count = len(lines)
        
        # Chuẩn hóa từng dòng
        normalized_lines = []
        for line in lines:
            # Xóa khoảng trắng đầu/cuối dòng
            line = line.strip()
            
            # Bỏ qua dòng trống
            if not line:
                continue
            
            # Xóa dấu cách thừa (nhiều space → 1 space)
            line = re.sub(r'\s+', ' ', line)
            
            normalized_lines.append(line)
        
        # Ghi đè file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(normalized_lines))
        
        new_line_count = len(normalized_lines)
        print(f"   ✅ {original_line_count} dòng → {new_line_count} dòng (đã xóa {original_line_count - new_line_count} dòng)")
        
        return original_line_count, new_line_count
        
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
        return 0, 0


def merge_chapter_titles(file_path: Path) -> int:
    """
    Ghép các dòng "Chương I/II/III/IV..." với tiêu đề chương phía sau
    
    Pattern:
    Chương I
    TIÊU ĐỀ CHƯƠNG
    
    → Chương I: TIÊU ĐỀ CHƯƠNG
    
    Returns:
        Số lượng dòng đã ghép
    """
    print(f"📄 Đang xử lý ghép chương: {file_path.name}")
    
    try:
        # Đọc file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        merged_lines = []
        merged_count = 0
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Kiểm tra pattern "Chương I/II/III/..." hoặc "CHƯƠNG I/II/..."
            # Dùng regex để match các số La Mã
            chapter_pattern = re.match(r'^(CHƯƠNG|Chương)\s+([IVXLCDM]+)$', line, re.IGNORECASE)
            
            if chapter_pattern and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                
                # Nếu dòng tiếp theo không rỗng và không phải là pattern khác
                if next_line and not re.match(r'^(CHƯƠNG|Chương|Điều|Mục)\s+', next_line, re.IGNORECASE):
                    # Ghép thành "Chương X: TIÊU ĐỀ"
                    chapter_num = chapter_pattern.group(2)
                    merged_line = f"CHƯƠNG {chapter_num}: {next_line}"
                    merged_lines.append(merged_line)
                    merged_count += 1
                    i += 2  # Bỏ qua cả 2 dòng
                    continue
            
            # Không match pattern → giữ nguyên
            if line:
                merged_lines.append(line)
            i += 1
        
        # Ghi đè file
        if merged_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(merged_lines))
            print(f"   ✅ Đã ghép {merged_count} tiêu đề chương")
        else:
            print(f"   ℹ️  Không tìm thấy pattern cần ghép")
        
        return merged_count
        
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
        return 0


def main():
    """Duyệt qua tất cả file .txt trong raw_data/ và chuẩn hóa"""
    
    # Thư mục raw_data
    raw_data_dir = Path(__file__).parent / "raw_data"
    
    if not raw_data_dir.exists():
        print(f"❌ Không tìm thấy thư mục: {raw_data_dir}")
        return
    
    print(f"🔍 Quét thư mục: {raw_data_dir}\n")
    
    # Tìm tất cả file .txt
    txt_files = list(raw_data_dir.glob("*.txt"))
    
    if not txt_files:
        print("⚠️  Không tìm thấy file .txt nào")
        return
    
    print(f"📂 Tìm thấy {len(txt_files)} file .txt\n")
    
    # Thống kê
    total_original = 0
    total_normalized = 0
    total_merged = 0
    success_count = 0
    
    # Xử lý từng file
    for txt_file in sorted(txt_files):
        original, normalized = normalize_text_file(txt_file)
        if normalized > 0:
            success_count += 1
            total_original += original
            total_normalized += normalized
    
    print(f"\n{'='*60}")
    print(f"BƯỚC 2: Ghép tiêu đề chương")
    print(f"{'='*60}\n")
    
    # Ghép tiêu đề chương
    for txt_file in sorted(txt_files):
        merged = merge_chapter_titles(txt_file)
        total_merged += merged
    
    # Tổng kết
    print(f"\n{'='*60}")
    print(f"✅ Hoàn thành: {success_count}/{len(txt_files)} file")
    print(f"📊 Tổng số dòng: {total_original} → {total_normalized}")
    print(f"🗑️  Đã xóa: {total_original - total_normalized} dòng trống/thừa")
    print(f"🔗 Đã ghép: {total_merged} tiêu đề chương")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
