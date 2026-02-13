from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime
from app.models.inflation import InflationData
import requests

class InflationService:
    @staticmethod
    def get_inflation_data(
        db: Session,
        category: Optional[str] = None,
        source: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[InflationData]:
        """Get inflation data with filters"""
        query = db.query(InflationData)
        
        if category:
            query = query.filter(InflationData.category == category)
        if source:
            query = query.filter(InflationData.source == source)
        if start_date:
            query = query.filter(InflationData.period >= start_date)
        if end_date:
            query = query.filter(InflationData.period <= end_date)
        
        return query.order_by(InflationData.period.desc()).all()
    
    @staticmethod
    def get_latest_inflation(
        db: Session,
        category: Optional[str] = None
    ) -> Optional[InflationData]:
        """Get the latest inflation data"""
        query = db.query(InflationData)
        
        if category:
            query = query.filter(InflationData.category == category)
        
        return query.order_by(InflationData.period.desc()).first()
    
    @staticmethod
    def fetch_rbi_data() -> List[dict]:
        """Fetch RBI inflation data"""
        data = []
        try:
            # RBI API or data source
            # This is a placeholder - actual implementation would use RBI's API or data files
            # url = "https://www.rbi.org.in/Scripts/DataRepository.aspx"
            # response = requests.get(url, timeout=10)
            # Parse the response and extract inflation data
            pass
        except Exception as e:
            print(f"Error fetching RBI data: {e}")
        
        return data
    
    @staticmethod
    def fetch_mp_govt_data() -> List[dict]:
        """Fetch MP Government inflation data"""
        data = []
        try:
            # MP Govt API or data source
            # This is a placeholder - actual implementation would use MP Govt's data source
            # url = "https://mp.gov.in/api/inflation"
            # response = requests.get(url, timeout=10)
            pass
        except Exception as e:
            print(f"Error fetching MP Govt data: {e}")
        
        return data
    
    @staticmethod
    def create_inflation_record(
        db: Session,
        source: str,
        category: str,
        value: float,
        period: date,
        subcategory: Optional[str] = None,
        region: str = "MP"
    ) -> InflationData:
        """Create a new inflation data record"""
        record = InflationData(
            source=source,
            category=category,
            subcategory=subcategory,
            value=value,
            period=period,
            region=region
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

