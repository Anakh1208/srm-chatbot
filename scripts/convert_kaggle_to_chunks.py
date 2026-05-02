"""
Convert Kaggle Education Dataset to Chunks
Works with most CSV formats
"""
import pandas as pd
import json
import sys
from pathlib import Path

def convert_faq_to_chunks(csv_path: str, output_path: str):
    """
    Convert FAQ CSV to chunks
    Expected columns: Question, Answer (or similar)
    """
    print(f"\n📂 Loading {csv_path}...")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} rows")
    print(f"📊 Columns: {list(df.columns)}")
    
    # Detect question/answer columns
    question_col = None
    answer_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'question' in col_lower or 'query' in col_lower or 'q' == col_lower:
            question_col = col
        if 'answer' in col_lower or 'response' in col_lower or 'a' == col_lower:
            answer_col = col
    
    if not question_col or not answer_col:
        print(f"⚠️ Could not auto-detect columns. Available: {list(df.columns)}")
        print(f"Please specify manually:")
        question_col = input("Question column name: ")
        answer_col = input("Answer column name: ")
    
    print(f"\n✅ Using columns: {question_col} | {answer_col}")
    
    # Create chunks
    chunks = []
    for idx, row in df.iterrows():
        question = str(row[question_col]).strip()
        answer = str(row[answer_col]).strip()
        
        if question and answer and question != 'nan' and answer != 'nan':
            # Combined text for better context
            text = f"Q: {question}\nA: {answer}"
            
            chunks.append({
                'text': text,
                'metadata': {
                    'chunk_id': idx,
                    'source': 'kaggle_faq',
                    'question': question,
                    'answer': answer
                }
            })
    
    print(f"\n✅ Created {len(chunks)} chunks")
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to {output_path}")
    
    # Preview
    if chunks:
        print(f"\n📄 Sample chunk:")
        print(f"   {chunks[0]['text'][:200]}...")


def convert_course_catalog_to_chunks(csv_path: str, output_path: str):
    """
    Convert course catalog CSV to chunks
    Expected columns: Course Code, Course Name, Description, etc.
    """
    print(f"\n📂 Loading {csv_path}...")
    
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} rows")
    print(f"📊 Columns: {list(df.columns)}")
    
    chunks = []
    
    for idx, row in df.iterrows():
        # Build text from all columns
        text_parts = []
        
        for col in df.columns:
            value = str(row[col]).strip()
            if value and value != 'nan':
                text_parts.append(f"{col}: {value}")
        
        text = "\n".join(text_parts)
        
        if text:
            chunks.append({
                'text': text,
                'metadata': {
                    'chunk_id': idx,
                    'source': 'kaggle_courses',
                    'type': 'course_info'
                }
            })
    
    print(f"\n✅ Created {len(chunks)} chunks")
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to {output_path}")


def main():
    print("\n" + "="*70)
    print("🎓 KAGGLE DATASET → CHUNKS CONVERTER")
    print("="*70)
    
    # Get input file
    if len(sys.argv) < 2:
        csv_path = input("\nEnter path to Kaggle CSV file: ")
    else:
        csv_path = sys.argv[1]
    
    if not Path(csv_path).exists():
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)
    
    # Output path
    project_root = Path(__file__).parent.parent
    output_path = project_root / "data" / "processed" / "kaggle_chunks.json"
    
    # Ask dataset type
    print("\n📋 Dataset Type:")
    print("1. FAQ (Question/Answer)")
    print("2. Course Catalog")
    print("3. General (will use all columns)")
    
    choice = input("\nSelect type (1/2/3): ")
    
    if choice == "1":
        convert_faq_to_chunks(csv_path, str(output_path))
    elif choice == "2":
        convert_course_catalog_to_chunks(csv_path, str(output_path))
    else:
        convert_course_catalog_to_chunks(csv_path, str(output_path))
    
    print("\n" + "="*70)
    print("✅ CONVERSION COMPLETE!")
    print("="*70)
    print(f"\n📁 Output: {output_path}")
    print(f"\n🎯 Next steps:")
    print(f"   1. Review chunks: cat {output_path}")
    print(f"   2. Build vector store: python scripts/build_vectorstore.py")
    print(f"   3. Test chatbot!")
    print()


if __name__ == "__main__":
    main()