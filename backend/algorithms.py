def insertion_sort(notes):
    result = notes.copy()

    for i in range(1, len(result)):
        current = result[i]
        current_title = (current.get("title") or "").lower()

        j = i - 1

        while j >= 0:
            previous_title = (
                result[j].get("title") or ""
            ).lower()

            if previous_title <= current_title:
                break

            result[j + 1] = result[j]
            j -= 1

        result[j + 1] = current

    return result


def insertion_sort_by_key(notes, key):
    result = notes.copy()

    for i in range(1, len(result)):
        current = result[i]
        current_value = current.get(key, 0)

        j = i - 1

        while j >= 0:
            previous_value = result[j].get(key, 0)

            if previous_value >= current_value:
                break

            result[j + 1] = result[j]
            j -= 1

        result[j + 1] = current

    return result


def binary_search_iterative(titles, target):
    target = target.strip().lower()

    left = 0
    right = len(titles) - 1

    while left <= right:
        middle = (left + right) // 2

        current = (
            titles[middle] or ""
        ).strip().lower()

        if current == target:
            return middle

        if current < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def binary_search_recursive(
    titles,
    target,
    left,
    right,
):
    target = target.strip().lower()

    if left > right:
        return -1

    middle = (left + right) // 2

    current = (
        titles[middle] or ""
    ).strip().lower()

    if current == target:
        return middle

    if current < target:
        return binary_search_recursive(
            titles,
            target,
            middle + 1,
            right,
        )

    return binary_search_recursive(
        titles,
        target,
        left,
        middle - 1,
    )


def linear_search(notes, key, value):
    search_value = str(
        value or ""
    ).strip().lower()

    for note in notes:
        note_value = note.get(key)

        if note_value is None:
            continue

        if (
            str(note_value)
            .strip()
            .lower()
            == search_value
        ):
            return note

    return None


def linear_search_tag(notes, tag):
    tag = (
        tag or ""
    ).strip().lower()

    for note in notes:
        note_tag = note.get("tag")

        if note_tag is None:
            continue

        note_tag = (
            str(note_tag)
            .strip()
            .lower()
        )

        if note_tag == tag:
            return note

    return None


def binary_search_title(
    sorted_notes,
    title,
):
    query = (title or "").strip().lower()

    for note in sorted_notes:
        note_title = (note.get("title") or "").strip().lower()

        if query in note_title:
            return note

    return {
        "message": "Note not found"
    }


def binary_search_tag(sorted_notes, tag):
    tag = str(tag or '').strip().lower()

    results = []

    for note in sorted_notes:
        note_tag = str(note.get('tag') or '').strip().lower()

        if note_tag == tag:
            results.append(note)

    if results:
        return results

    return {
        'message': 'No note found for this tag'
    }

