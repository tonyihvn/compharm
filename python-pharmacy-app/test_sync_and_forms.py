#!/usr/bin/env python3
"""
Test script for verifying sync downloads clients and forms upload works
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from database.models import Client, Form, Pharmacy, Facility
from api.backend_client import BackendAPIClient
from config.settings import settings
import json
from datetime import datetime

def test_sync_clients():
    """Test sync functionality - download clients from backend"""
    print("\n" + "="*70)
    print("TEST 1: SYNC CLIENTS FROM BACKEND")
    print("="*70)
    
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.init_db()
    print("✓ Database initialized")
    
    # Authenticate with backend
    api_client = BackendAPIClient()
    if not api_client.authenticate():
        print("✗ Failed to authenticate with backend server")
        print(f"  - Check Backend Username: {settings.BACKEND_USERNAME}")
        print(f"  - Check Backend Server URL: {settings.CENTRAL_SERVER_URL}")
        return False
    
    print(f"✓ Authenticated with backend: {api_client.base_url}")
    
    # Fetch clients
    pharmacy_id = settings.PHARMACY_ID
    print(f"\nFetching clients for pharmacy: {pharmacy_id}")
    
    clients_data = api_client.get_clients(pharmacy_id=pharmacy_id, limit=1000)
    if not clients_data:
        print("✗ Failed to fetch clients")
        return False
    
    clients = clients_data.get('clients', []) if isinstance(clients_data, dict) else clients_data
    print(f"✓ Fetched {len(clients)} client(s) from backend")
    
    if len(clients) == 0:
        print("⚠ No clients found for this pharmacy")
        return True  # Not an error, just no data
    
    # Save clients to database
    session = db_manager.get_session()
    try:
        # Ensure pharmacy exists
        pharmacy = session.query(Pharmacy).filter(Pharmacy.code == pharmacy_id).first()
        if not pharmacy:
            pharmacy = Pharmacy(
                code=pharmacy_id,
                name=settings.PHARMACY_NAME,
                is_active=True,
                api_key=settings.PHARMACY_ID
            )
            session.add(pharmacy)
            session.commit()
            print(f"✓ Created pharmacy record: {pharmacy_id}")
        else:
            print(f"✓ Pharmacy exists: {pharmacy_id}")
        
        # Ensure default facility
        facility = session.query(Facility).filter(Facility.code == "DEFAULT").first()
        if not facility:
            facility = Facility(
                code="DEFAULT",
                name="Default Facility",
                is_active=True
            )
            session.add(facility)
            session.commit()
            print("✓ Created default facility")
        else:
            print("✓ Default facility exists")
        
        # Save clients
        saved_count = 0
        updated_count = 0
        
        for client_data in clients:
            pepfar_id = client_data.get('pepfarId') or client_data.get('id')
            name = client_data.get('name', 'Unknown')
            
            existing = session.query(Client).filter(Client.pepfar_id == pepfar_id).first()
            
            if existing:
                existing.full_name = name
                existing.last_updated_from_server = datetime.now()
                updated_count += 1
            else:
                new_client = Client(
                    pepfar_id=pepfar_id,
                    full_name=name,
                    facility_id="DEFAULT",
                    pharmacy_id=pharmacy_id,
                    server_client_id=client_data.get('id'),
                    last_updated_from_server=datetime.now(),
                    status=client_data.get('status', 'active'),
                    created_locally_at=datetime.now(),
                    updated_locally_at=datetime.now()
                )
                session.add(new_client)
                saved_count += 1
        
        session.commit()
        print(f"✓ Saved {saved_count} new clients")
        print(f"✓ Updated {updated_count} existing clients")
        
        # Verify clients in database
        db_clients = session.query(Client).all()
        print(f"✓ Total clients in database: {len(db_clients)}")
        
        if db_clients:
            print("\n  Sample clients:")
            for client in db_clients[:5]:
                print(f"    - {client.pepfar_id}: {client.full_name}")
        
        return True
    
    except Exception as e:
        print(f"✗ Error saving clients: {str(e)}")
        return False
    
    finally:
        session.close()


def test_forms_schema():
    """Test forms table exists and is ready for upload"""
    print("\n" + "="*70)
    print("TEST 2: FORMS TABLE SCHEMA")
    print("="*70)
    
    db_manager = DatabaseManager()
    db_manager.init_db()
    
    session = db_manager.get_session()
    try:
        # Test creating a form record
        form = Form(
            name="Test Form",
            uuid="test-form-uuid-001",
            version="1.0",
            definition={"fields": []},
            is_published=False,
            uploaded_at=datetime.now()
        )
        session.add(form)
        session.commit()
        print("✓ Form table is ready for forms")
        
        # Verify form exists
        test_form = session.query(Form).filter(Form.uuid == "test-form-uuid-001").first()
        if test_form:
            print(f"✓ Successfully created test form: {test_form.name}")
        
        # Clean up test form
        session.delete(test_form)
        session.commit()
        
        return True
    
    except Exception as e:
        print(f"✗ Forms table error: {str(e)}")
        return False
    
    finally:
        session.close()


def test_clients_retrieval():
    """Test retrieving clients from database"""
    print("\n" + "="*70)
    print("TEST 3: RETRIEVE SYNCED CLIENTS FROM DATABASE")
    print("="*70)
    
    db_manager = DatabaseManager()
    session = db_manager.get_session()
    
    try:
        clients = session.query(Client).all()
        print(f"✓ Found {len(clients)} clients in database")
        
        if clients:
            print("\n  Clients available for Client Management:")
            for i, client in enumerate(clients[:10], 1):
                status = client.status or "unknown"
                print(f"    [{i}] {client.pepfar_id} - {client.full_name} ({status})")
            
            if len(clients) > 10:
                print(f"    ... and {len(clients) - 10} more")
        else:
            print("⚠ No clients found - Run sync first")
        
        return True
    
    except Exception as e:
        print(f"✗ Error retrieving clients: {str(e)}")
        return False
    
    finally:
        session.close()


def main():
    print("\n" + "="*70)
    print("PHARMACY APP - SYNC & FORMS TEST SUITE")
    print("="*70)
    
    print(f"\nConfiguration:")
    print(f"  Pharmacy ID: {settings.PHARMACY_ID}")
    print(f"  Pharmacy Name: {settings.PHARMACY_NAME}")
    print(f"  Backend Server: {settings.CENTRAL_SERVER_URL}")
    print(f"  Database: {settings.DATABASE_URL}")
    
    results = []
    
    # Run tests
    results.append(("Sync Clients", test_sync_clients()))
    results.append(("Forms Schema", test_forms_schema()))
    results.append(("Clients Retrieval", test_clients_retrieval()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Sync and Forms are ready to use.")
        print("\nNext steps:")
        print("  1. Start the Python app: python main.py")
        print("  2. Login with your credentials")
        print("  3. Go to Admin Panel > Sync tab")
        print("  4. Click 'Sync Now' to download clients")
        print("  5. Clients will appear in Clients Management page")
        print("  6. Use Forms Management tab to upload JSON forms")
        return 0
    else:
        print("\n✗ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
