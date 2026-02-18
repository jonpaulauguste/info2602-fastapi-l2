import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import or_, select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

# test

@cli.command(help="Recreate the database and insert a default user (bob).")
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User(username='bob', email='bob@gmail.com', password='bobpass')
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command(help="Get a user by username.")
def get_user(username:str):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command(help="Get all users.")
def get_all_users():
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command(help="Change a user's email.")
def change_email(username: str, new_email:str):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command(help="Create a new user.")
def create_user(username: str, email:str, password: str):
    with get_session() as db: # Get a connection to the database
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() #let the database undo any previous steps of a transaction
            #print(e.orig) #optionally print the error raised by the database
            print("Username or email already taken!") #give the user a useful message
        else:
            print(newuser) # print the newly created user

@cli.command(help="Delete a user by username.")
def delete_user(username: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

@cli.command(help="Search for users by partial username or email match.")
def search_user(query: str):
    with get_session() as db:
        users = db.exec(
            select(User).where(
                or_(
                    User.username.like(f"%{query}%"),
                    User.email.like(f"%{query}%")
                )
            )
        ).all()

        if not users:
            print("No matching users found.")
        else:
            for user in users:
                print(user)

@cli.command(help="List users with pagination support.")
def list_users(limit: int = 10, offset: int = 0):
    with get_session() as db:
        users = db.exec(
            select(User)
            .offset(offset)
            .limit(limit)
        ).all()

        if not users:
            print("No users found.")
        else:
            for user in users:
                print(user)




if __name__ == "__main__":
    cli()