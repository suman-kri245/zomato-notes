from database import SessionLocal
import models


SEED_USERS = [
    {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "password": "alicepass123",
    },
    {
        "id": 2,
        "name": "Bob",
        "email": "bob@example.com",
        "password": "bobpass123",
    },
]


SEED_NOTES = [
    {
        "id": 1,
        "owner_id": 1,
        "title": "Standup Summary",
        "tag": "work",
        "content": "Discussed sprint progress, blockers on the payments API integration, and the plan for the demo on Friday.",
    },
    {
        "id": 2,
        "owner_id": 1,
        "title": "Sprint Retro Notes",
        "tag": "work",
        "content": "Retro highlighted communication gaps between frontend and backend teams and agreed on daily syncs going forward.",
    },
    {
        "id": 3,
        "owner_id": 2,
        "title": "One on One",
        "tag": "work",
        "content": "Quick check-in, no blockers, discussed career growth goals for next quarter.",
    },
    {
        "id": 4,
        "owner_id": 1,
        "title": "Morning Run",
        "tag": "health",
        "content": "Ran 5km along the river trail before breakfast, felt great.",
    },
    {
        "id": 5,
        "owner_id": 2,
        "title": "Doctor Visit",
        "tag": "health",
        "content": "Annual checkup went well, blood pressure normal, scheduled next visit in six months.",
    },
    {
        "id": 6,
        "owner_id": 1,
        "title": "Pasta Recipe",
        "tag": "recipes",
        "content": "Boil pasta, saute garlic in olive oil, add tomatoes, basil, and a pinch of chili flakes.",
    },
    {
        "id": 7,
        "owner_id": 2,
        "title": "Smoothie Recipe",
        "tag": "recipes",
        "content": "Blend banana, spinach, almond milk, and a spoon of peanut butter for breakfast.",
    },
    {
        "id": 8,
        "owner_id": 1,
        "title": "Flight Booking",
        "tag": "travel",
        "content": "Booked a round trip flight for the December vacation, window seat confirmed.",
    },
    {
        "id": 9,
        "owner_id": 2,
        "title": "Random Thought",
        "tag": "random",
        "content": "Maybe the library needs a better recommendation system based on reading history.",
    },
    {
        "id": 10,
        "owner_id": 1,
        "title": "Quote To Remember",
        "tag": "random",
        "content": "Done is better than perfect, keep shipping.",
    },
]


# Part 2 Ranking Dataset
RANKING_DATASET = [
    {
        "title": "Apple Harvest Notes",
        "content": "The apple orchard yielded a strong apple harvest this season with apple crates ready.",
    },
    {
        "title": "Budget Draft",
        "content": "Quarterly budget review shows spending under control across all departments.",
    },
    {
        "title": "Coffee Tasting",
        "content": "Sampled three coffee blends today, the dark roast coffee stood out the most.",
    },
    {
        "title": "Daily Standup",
        "content": "Team standup covered blockers, progress, and the plan for tomorrow.",
    },
    {
        "title": "Evening Walk",
        "content": "Took a long evening walk around the park to clear my head.",
    },
    {
        "title": "Fruit Basket Plan",
        "content": "Planning a fruit basket with apple, banana, and orange slices for the event.",
    },
    {
        "title": "Garden Update",
        "content": "The garden apple tree is finally blooming after the apple tree pruning last month.",
    },
    {
        "title": "History Reading",
        "content": "Continued reading the history book about ancient trade routes.",
    },
    {
        "title": "Invoice Follow-up",
        "content": "Sent a follow-up email regarding the pending invoice payment.",
    },
    {
        "title": "Journal Entry",
        "content": "Reflected on the week's progress and set goals for next week.",
    },
    {
        "title": "Kitchen Inventory",
        "content": "Checked the kitchen inventory; running low on coffee and sugar.",
    },
    {
        "title": "Language Practice",
        "content": "Practiced twenty new vocabulary words during today's language session.",
    },
]


def seed_database():

    db = SessionLocal()

    try:

        # -------------------------
        # USERS
        # -------------------------

        if db.query(models.User).count() == 0:

            for user in SEED_USERS:
                db.add(models.User(**user))

            db.commit()

            print("Users Seeded Successfully")

        else:

            print("Users already exist")


        # -------------------------
        # ORIGINAL NOTES
        # -------------------------

        if db.query(models.Note).count() == 0:

            for note in SEED_NOTES:
                db.add(models.Note(**note))

            db.commit()

            print("Original Notes Seeded Successfully")

        else:

            print("Notes already exist")


        # -------------------------
        # PART 2 RANKING DATASET
        # -------------------------

        existing_titles = {
            note.title
            for note in db.query(models.Note).all()
        }

        added_count = 0

        for item in RANKING_DATASET:

            if item["title"] not in existing_titles:

                note = models.Note(
                    title=item["title"],
                    content=item["content"],
                    tag="kb-demo",
                    owner_id=1,
                )

                db.add(note)
                added_count += 1

        if added_count > 0:

            db.commit()

            print(
                f"Ranking Dataset Added Successfully: {added_count} notes"
            )

        else:

            print("Ranking Dataset already exists")


        print("Database Seeding Completed Successfully")


    except Exception as e:

        db.rollback()

        print("Seeding Error:", e)

        raise


    finally:

        db.close()


if __name__ == "__main__":

    seed_database()