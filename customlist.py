class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class LinkedListQueue:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def add(self, key, value):
        new_node = Node(key, value)
        if self.tail:
            self.tail.next = new_node
            self.tail = new_node
        else:
            self.head = self.tail = new_node
        self.size += 1

    def pop(self):
        if self.head:
            key = self.head.key
            value = self.head.value
            self.head = self.head.next
            self.size -= 1
            return key, value
        return None

    def remove_by_key(self, key):
        current = self.head
        previous = None
        
        while current:
            if current.key == key:
                if previous:
                    previous.next = current.next
                else:
                    self.head = current.next
                if current == self.tail:
                    self.tail = previous
                self.size -= 1
                return current.key, current.value
            previous = current
            current = current.next
        return None

    def peek(self):
        if self.head:
            return self.head.key, self.head.value
        return None

    def is_empty(self):
        return self.size == 0
