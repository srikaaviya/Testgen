def removeKthFromEnd(head, k):
    if not head or k == 0:
        return head

    fast, slow = head, head

    for _ in range(k):
        if not fast:       # k > number of nodes, invalid
            return head
        fast = fast.next

    # k == n: remove head
    if not fast:
        return head.next

    while fast.next:
        fast = fast.next
        slow = slow.next

    slow.next = slow.next.next
    return head