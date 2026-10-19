def chunk_text(
    text: str,
    max_chars: int = 800
) -> list[str]:
    
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        
        if not paragraph:
            continue
        
        # Split paragraphs that exceed limit
        while len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
                
            chunks.append(paragraph[:max_chars])
            paragraph = paragraph[max_chars:]
            
        if not paragraph:
            continue
        
        candidate = (
            current + "\n\n" + paragraph
            if current else paragraph
        )
        
        if len(candidate) > max_chars:
            if current:
                chunks.append(current)
                
            current = paragraph
        else:
            current = candidate
            
    if current:
        chunks.append(current)
            
    return chunks