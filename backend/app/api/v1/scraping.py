from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.geospatial import Locality
import subprocess
import os

router = APIRouter(prefix="/scraping", tags=["scraping"])

@router.post("/bhopal/rent")
def scrape_bhopal_rent(db: Session = Depends(get_db)):
    """Trigger web scraping for Bhopal rent data"""
    try:
        # Use absolute path from /app directory (Docker container)
        script_path = '/app/scrape_bhopal.py'
        
        if not os.path.exists(script_path):
            raise HTTPException(
                status_code=404,
                detail=f"Scraping script not found at {script_path}"
            )
        
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
            cwd='/app'
        )
        
        if result.returncode == 0:
            # Count scraped listings
            from app.models.rent import RentListing
            count = db.query(RentListing).filter(
                RentListing.source == 'nobroker'
            ).count()
            
            return {
                "status": "success",
                "message": "Bhopal rent scraping completed",
                "listings_found": count,
                "output": result.stdout[-500:]  # Last 500 chars
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Scraping failed: {result.stderr}"
            )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail="Scraping timeout - process took too long"
        )
    except subprocess.TimeoutExpired as e:
        raise HTTPException(
            status_code=408,
            detail=f"Scraping timeout: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_msg = f"Error running scraper: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

@router.post("/bhopal/grocery")
def scrape_bhopal_grocery(db: Session = Depends(get_db)):
    """Trigger web scraping for Bhopal grocery data"""
    try:
        script_path = '/app/scrape_bhopal.py'
        
        if not os.path.exists(script_path):
            raise HTTPException(
                status_code=404,
                detail=f"Scraping script not found at {script_path}"
            )
        
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=300,
            cwd='/app'
        )
        
        if result.returncode == 0:
            from app.models.grocery import GroceryItem, GroceryStore
            count = db.query(GroceryItem).filter(
                GroceryItem.store_id.in_(
                    db.query(GroceryStore.id).filter(GroceryStore.name == 'BigBasket')
                )
            ).count()
            
            return {
                "status": "success",
                "message": "Bhopal grocery scraping completed",
                "products_found": count
            }
        else:
            error_detail = result.stderr or result.stdout or "Unknown error"
            raise HTTPException(
                status_code=500,
                detail=f"Scraping failed (exit code {result.returncode}): {error_detail[-500:]}"
            )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Scraping timeout")
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}\n{traceback.format_exc()[-500:]}"
        )

@router.post("/bhopal/all")
def scrape_bhopal_all(db: Session = Depends(get_db)):
    """Trigger complete web scraping for all Bhopal data"""
    try:
        # Use absolute path from /app directory (Docker container)
        script_path = '/app/scrape_bhopal.py'
        
        # Check if file exists
        if not os.path.exists(script_path):
            raise HTTPException(
                status_code=404,
                detail=f"Scraping script not found at {script_path}"
            )
        
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes for all data
            cwd='/app'  # Set working directory
        )
        
        if result.returncode == 0:
            from app.models.rent import RentListing
            from app.models.grocery import GroceryItem
            
            rent_count = db.query(RentListing).filter(
                RentListing.locality_id.in_(
                    db.query(Locality.id).filter(Locality.city == 'Bhopal')
                )
            ).count()
            
            grocery_count = db.query(GroceryItem).count()
            
            return {
                "status": "success",
                "message": "Bhopal scraping completed",
                "rent_listings": rent_count,
                "grocery_products": grocery_count,
                "output": result.stdout[-1000:] if result.stdout else "No output"
            }
        else:
            error_detail = result.stderr or result.stdout or "Unknown error"
            raise HTTPException(
                status_code=500,
                detail=f"Scraping failed (exit code {result.returncode}): {error_detail[-500:]}"
            )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail="Scraping timeout - process took longer than 10 minutes"
        )
    except Exception as e:
        import traceback
        error_msg = f"Error running scraper: {str(e)}\n{traceback.format_exc()[-500:]}"
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

