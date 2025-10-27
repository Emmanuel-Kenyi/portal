import pytest
import threading
import time
import random
from django.db import transaction, connection
from django.db.utils import OperationalError
from django.db.models import F, Value
from django.db.models.functions import Concat
from clubs.models import Club

def rename_club_atomic(club, suffix):
    """Perform a single atomic DB-side append to description (safe)."""
    with transaction.atomic():
        Club.objects.filter(pk=club.pk).update(
            description=Concat(F('description'), Value(suffix))
        )

def rename_club_with_retries(club, suffix):
    """Thread target with retries for sqlite locking."""
    max_retries = 6
    for attempt in range(1, max_retries + 1):
        try:
            rename_club_atomic(club, suffix)
            return
        except OperationalError as e:
            if 'locked' in str(e).lower() and attempt < max_retries:
                time.sleep(random.uniform(0.01, 0.05) * attempt)
                continue
            raise

@pytest.mark.django_db
def test_concurrent_club_updates(club):
    """
    Try to simulate concurrent updates. On sqlite we perform sequential atomic updates
    (sqlite has poor row-locking across threads), otherwise use threads.
    """
    worker_count = 3

    if connection.vendor == "sqlite":
        # avoid sqlite table-locked issues by performing repeated atomic updates
        for _ in range(worker_count):
            rename_club_atomic(club, "!")
    else:
        threads = [threading.Thread(target=rename_club_with_retries, args=(club, "!")) for _ in range(worker_count)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    club.refresh_from_db()
    assert club.description.endswith("!" * worker_count)
