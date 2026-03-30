#!/usr/bin/env python3
import json
from backend.core.rag_engine import RAGEngine

print('='*70)
print('SRM CHATBOT - COMPLETE DEMONSTRATION')
print('='*70)

print('\nPHASE 1: DATA COLLECTION')
print('-'*70)
raw_data = json.load(open('data/raw/scraped_data.json'))
processed_data = json.load(open('data/processed/chunks.json'))

print(f'Pages scraped: {len(raw_data)}')
print(f'Chunks processed: {len(processed_data)}')

print(f'\n{"="*70}')
print('PHASE 2: RAG ENGINE')
print('-'*70)

print('\nInitializing RAG Engine...')
rag = RAGEngine('data/vectorstore')
print('RAG Engine ready!\n')

queries = [
    'What programs does SRM offer?',
    'Tell me about admissions'
]

for i, query in enumerate(queries, 1):
    print(f'\n{"="*70}')
    print(f'Query {i}: {query}')
    print('='*70)
    
    result = rag.answer_question(query)
    
    print(f'\nANSWER: {result["answer"][:200]}...')
    print(f'SOURCES: {len(result["sources"])} found')

print(f'\n{"="*70}')
print('DEMO COMPLETE - SYSTEM WORKING!')
print('='*70)
