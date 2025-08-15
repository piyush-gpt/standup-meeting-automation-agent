#!/usr/bin/env python3
"""
Database initialization script for Auto Standup
Creates collections and indexes for the standup system
"""
from mongo import db
from pymongo import ASCENDING, DESCENDING
import os
from dotenv import load_dotenv

load_dotenv()

def create_collections_and_indexes():
    """Create all required collections and indexes"""
    print("🚀 Initializing Auto Standup Database...")
    
    # 1. Workspaces collection
    print("📁 Creating workspaces collection...")
    workspaces_col = db["workspaces"]
    
    # Create indexes for workspaces
    workspaces_col.create_index([("workspace_id", ASCENDING)], unique=True)
    workspaces_col.create_index([("installed_at", DESCENDING)])
    print("✅ Workspaces collection and indexes created")
    
    # 2. Users collection
    print("👥 Creating users collection...")
    users_col = db["users"]
    
    # Create indexes for users
    users_col.create_index([("workspace_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
    users_col.create_index([("workspace_id", ASCENDING)])
    users_col.create_index([("updated_at", DESCENDING)])
    print("✅ Users collection and indexes created")
    
    # 3. Standup runs collection
    print("🏃 Creating standup_runs collection...")
    runs_col = db["standup_runs"]
    
    # Create indexes for standup runs
    runs_col.create_index([("workspace_id", ASCENDING)])
    runs_col.create_index([("status", ASCENDING)])
    runs_col.create_index([("created_at", DESCENDING)])
    runs_col.create_index([("_id", ASCENDING)])
    print("✅ Standup runs collection and indexes created")
    
    # 4. Standup responses collection
    print("💬 Creating standup_responses collection...")
    responses_col = db["standup_responses"]
    
    # Create indexes for standup responses
    responses_col.create_index([("workspace_id", ASCENDING)])
    responses_col.create_index([("run_id", ASCENDING)])
    responses_col.create_index([("user_id", ASCENDING)])
    responses_col.create_index([("created_at", DESCENDING)])
    print("✅ Standup responses collection and indexes created")
    
    print("\n🎉 Database initialization completed successfully!")
    
    # Show collection stats
    print("\n📊 Collection Statistics:")
    print(f"Workspaces: {workspaces_col.count_documents({})}")
    print(f"Users: {users_col.count_documents({})}")
    print(f"Standup Runs: {runs_col.count_documents({})}")
    print(f"Standup Responses: {responses_col.count_documents({})}")

def create_sample_data():
    """Create sample data for testing"""
    print("\n🧪 Creating sample data for testing...")
    
    # Sample workspace
    sample_workspace = {
        "workspace_id": "sample_workspace_123",
        "workspace_name": "Sample Company",
        "bot_token": "xoxb-sample-token",
        "installer": "test_user",
        "installed_at": "2024-01-01T00:00:00Z"
    }
    
    # Sample users
    sample_users = [
        {
            "workspace_id": "sample_workspace_123",
            "user_id": "U1234567890",
            "real_name": "John Doe",
            "dm_channel_id": "D1234567890",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        {
            "workspace_id": "sample_workspace_123",
            "user_id": "U0987654321",
            "real_name": "Jane Smith",
            "dm_channel_id": "D0987654321",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ]
    
    try:
        # Insert sample workspace
        db["workspaces"].insert_one(sample_workspace)
        print("✅ Sample workspace created")
        
        # Insert sample users
        db["users"].insert_many(sample_users)
        print("✅ Sample users created")
        
        print("🎯 Sample data created successfully!")
        
    except Exception as e:
        print(f"⚠️  Sample data creation failed (this is normal if data already exists): {e}")

def drop_collections():
    """Drop all collections (use with caution!)"""
    print("⚠️  WARNING: This will delete all data!")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm == "DELETE":
        collections = ["workspaces", "users", "standup_runs", "standup_responses"]
        for collection_name in collections:
            db[collection_name].drop()
            print(f"🗑️  Dropped collection: {collection_name}")
        print("✅ All collections dropped")
    else:
        print("❌ Operation cancelled")

def show_collection_info():
    """Show information about existing collections"""
    print("\n📋 Collection Information:")
    
    collections = ["workspaces", "users", "standup_runs", "standup_responses"]
    
    for collection_name in collections:
        if collection_name in db.list_collection_names():
            collection = db[collection_name]
            count = collection.count_documents({})
            indexes = list(collection.list_indexes())
            
            print(f"\n📁 {collection_name}:")
            print(f"   Documents: {count}")
            print(f"   Indexes: {len(indexes)}")
            
            for idx in indexes:
                print(f"     - {idx['name']}: {idx['key']}")
        else:
            print(f"\n📁 {collection_name}: Not created yet")

if __name__ == "__main__":
    print("Auto Standup Database Initialization")
    print("====================================")
    
    # Check MongoDB connection
    try:
        # Test connection
        db.command("ping")
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("Please check your MONGO_URI and ensure MongoDB is running")
        exit(1)
    
    # Show current state
    show_collection_info()
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Create collections and indexes")
    print("2. Create sample data")
    print("3. Drop all collections (DANGER!)")
    print("4. Show collection info")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        create_collections_and_indexes()
    elif choice == "2":
        create_sample_data()
    elif choice == "3":
        drop_collections()
    elif choice == "4":
        show_collection_info()
    elif choice == "5":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")
