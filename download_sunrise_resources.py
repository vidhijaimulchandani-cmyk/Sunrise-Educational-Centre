#!/usr/bin/env python3
"""
Auto-generated download script for Sunrise Education Centre resources
Generated on: 2025-07-28 22:09:21
"""

import requests
import os
from urllib.parse import urlparse

def download_sunrise_resources():
    """Download all Google Drive resources from Sunrise Education Centre"""
    
    # Create download directory
    download_dir = "uploads/sunrise_education"
    os.makedirs(download_dir, exist_ok=True)
    
    # Resources to download
    resources = [
        {
            "filename": "Case-Study-All-Chapters_1mTuOHG3ah_AJ6kfdLciyumFMTOj50b78.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1mTuOHG3ah_AJ6kfdLciyumFMTOj50b78",
            "title": "Case Study (All Chapters)",
            "file_id": "1mTuOHG3ah_AJ6kfdLciyumFMTOj50b78"
        },
        {
            "filename": "Basic-2024-2025-with-Solution_1AKPa-z8EfdV6zrV7iLBrlJ_PYlZh1nMX.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1AKPa-z8EfdV6zrV7iLBrlJ_PYlZh1nMX",
            "title": "Basic (2024-2025) with Solution",
            "file_id": "1AKPa-z8EfdV6zrV7iLBrlJ_PYlZh1nMX"
        },
        {
            "filename": "Standard-2024-2025-with-solution_13vras5PqieLebe_nLadoHUr6dlGksPK7.pdf",
            "url": "https://drive.google.com/uc?export=download&id=13vras5PqieLebe_nLadoHUr6dlGksPK7",
            "title": "Standard (2024-2025) with solution",
            "file_id": "13vras5PqieLebe_nLadoHUr6dlGksPK7"
        },
        {
            "filename": "CH-1-Real-Number_1KEjd1PtHmhECYmtIVAIMzdCmLCfRS0jT.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1KEjd1PtHmhECYmtIVAIMzdCmLCfRS0jT",
            "title": "CH 1 - Real Number",
            "file_id": "1KEjd1PtHmhECYmtIVAIMzdCmLCfRS0jT"
        },
        {
            "filename": "CH-2-Polynomials_1a_AQAjO0fnGB_tASwoy7QbvVqv8ypo2M.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1a_AQAjO0fnGB_tASwoy7QbvVqv8ypo2M",
            "title": "CH 2 - Polynomials",
            "file_id": "1a_AQAjO0fnGB_tASwoy7QbvVqv8ypo2M"
        },
        {
            "filename": "CH-3-Pair-of-Linear-Equations-in-Two-Variables_13rZw4nDD7LV9hXhYi5J-2uCvsrRWU7ZZ.pdf",
            "url": "https://drive.google.com/uc?export=download&id=13rZw4nDD7LV9hXhYi5J-2uCvsrRWU7ZZ",
            "title": "CH 3 - Pair of Linear Equations in Two Variables",
            "file_id": "13rZw4nDD7LV9hXhYi5J-2uCvsrRWU7ZZ"
        },
        {
            "filename": "CH-4-Quadratic-Equation_1vhZG00hT90c2-0FEWU2C57EpQlb4pLSa.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1vhZG00hT90c2-0FEWU2C57EpQlb4pLSa",
            "title": "CH 4 - Quadratic Equation",
            "file_id": "1vhZG00hT90c2-0FEWU2C57EpQlb4pLSa"
        },
        {
            "filename": "CH-5-Arithmetic-Progression_11V7i3_2sJ7RZNstTXbjlFrX0sanN3MZ9.pdf",
            "url": "https://drive.google.com/uc?export=download&id=11V7i3_2sJ7RZNstTXbjlFrX0sanN3MZ9",
            "title": "CH 5 - Arithmetic Progression",
            "file_id": "11V7i3_2sJ7RZNstTXbjlFrX0sanN3MZ9"
        },
        {
            "filename": "CH-6-Triangles_1dP3TFuMNxz9I25O1s2RDbeG0GKQ_Y_Nf.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1dP3TFuMNxz9I25O1s2RDbeG0GKQ_Y_Nf",
            "title": "CH 6 - Triangles",
            "file_id": "1dP3TFuMNxz9I25O1s2RDbeG0GKQ_Y_Nf"
        },
        {
            "filename": "CH-7-Coordinate-Geometry_1e-dNaC2Skk9-dta6SNLvof-kpZC3Aswd.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1e-dNaC2Skk9-dta6SNLvof-kpZC3Aswd",
            "title": "CH 7 - Coordinate Geometry",
            "file_id": "1e-dNaC2Skk9-dta6SNLvof-kpZC3Aswd"
        },
        {
            "filename": "CH-8-Trigonometry_1nsH_Go7nxXasSX0HWoYSad9aUCl-vDfO.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1nsH_Go7nxXasSX0HWoYSad9aUCl-vDfO",
            "title": "CH 8 - Trigonometry",
            "file_id": "1nsH_Go7nxXasSX0HWoYSad9aUCl-vDfO"
        },
        {
            "filename": "CH-9-Applications-of-Trigonometry_1oTnQH30HPoBKEHOicZ0c7MXrDP4GduGg.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1oTnQH30HPoBKEHOicZ0c7MXrDP4GduGg",
            "title": "CH 9 - Applications of Trigonometry",
            "file_id": "1oTnQH30HPoBKEHOicZ0c7MXrDP4GduGg"
        },
        {
            "filename": "CH-10-Circles_1CC5TaIgJTR3ZuB6BHUDmWIXYDmZ2_VAo.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1CC5TaIgJTR3ZuB6BHUDmWIXYDmZ2_VAo",
            "title": "CH 10 - Circles",
            "file_id": "1CC5TaIgJTR3ZuB6BHUDmWIXYDmZ2_VAo"
        },
        {
            "filename": "CH-11-Areas-Related-to-Circles_1NGuipqjtxnpArlQZtddD88C1rC2dyFzB.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1NGuipqjtxnpArlQZtddD88C1rC2dyFzB",
            "title": "CH 11 - Areas Related to Circles",
            "file_id": "1NGuipqjtxnpArlQZtddD88C1rC2dyFzB"
        },
        {
            "filename": "CH-12-Surface-Areas-Volumes_1oS693cOTkYhY8PUn5w-NDBf9mL_mCa86.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1oS693cOTkYhY8PUn5w-NDBf9mL_mCa86",
            "title": "CH 12 - Surface Areas & Volumes",
            "file_id": "1oS693cOTkYhY8PUn5w-NDBf9mL_mCa86"
        },
        {
            "filename": "CH-13-Statistics_1WblRmjMTLvxwsF-y3_9KECE8Xh51qIpu.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1WblRmjMTLvxwsF-y3_9KECE8Xh51qIpu",
            "title": "CH 13 - Statistics",
            "file_id": "1WblRmjMTLvxwsF-y3_9KECE8Xh51qIpu"
        },
        {
            "filename": "CH-14-Probability_1jRVyAa184Jz-FxxuDDguZMJPkxCZymUf.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1jRVyAa184Jz-FxxuDDguZMJPkxCZymUf",
            "title": "CH 14 - Probability",
            "file_id": "1jRVyAa184Jz-FxxuDDguZMJPkxCZymUf"
        },
        {
            "filename": "Polynomials-Worksheet-UNLOCKED_1ZgUSqxEoH3KnobfrlOKtsQGzCHfoC_cM.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1ZgUSqxEoH3KnobfrlOKtsQGzCHfoC_cM",
            "title": "Polynomials - Worksheet (UNLOCKED)",
            "file_id": "1ZgUSqxEoH3KnobfrlOKtsQGzCHfoC_cM"
        },
        {
            "filename": "Triangles-Worksheet-UNLOCKED_11SIma-Eu2ljYlWAKSFpS04tCyqAjij7z.pdf",
            "url": "https://drive.google.com/uc?export=download&id=11SIma-Eu2ljYlWAKSFpS04tCyqAjij7z",
            "title": "Triangles - Worksheet (UNLOCKED)",
            "file_id": "11SIma-Eu2ljYlWAKSFpS04tCyqAjij7z"
        },
        {
            "filename": "Probability-Worksheet-UNLOCKED_1iluMHbcoJX73DZe-oe7-a500yv7OHiAB.pdf",
            "url": "https://drive.google.com/uc?export=download&id=1iluMHbcoJX73DZe-oe7-a500yv7OHiAB",
            "title": "Probability - Worksheet (UNLOCKED)",
            "file_id": "1iluMHbcoJX73DZe-oe7-a500yv7OHiAB"
        },
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    successful = 0
    failed = 0
    
    for i, resource in enumerate(resources, 1):
        try:
            print(f"Downloading {{i}}/{{len(resources)}}: {{resource['title']}}")
            
            response = session.get(resource['url'], stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(download_dir, resource['filename'])
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(filepath)
            print(f"✅ Downloaded: {{resource['filename']}} ({{file_size}} bytes)")
            successful += 1
            
        except Exception as e:
            print(f"❌ Failed to download {{resource['title']}}: {{e}}")
            failed += 1
    
    print(f"\nDownload Summary:")
    print(f"✅ Successful: {{successful}}")
    print(f"❌ Failed: {{failed}}")
    print(f"📁 Files saved to: {{download_dir}}")

if __name__ == "__main__":
    download_sunrise_resources()
