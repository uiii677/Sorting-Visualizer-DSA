from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# --- Sorting Algorithms ---

def bubble_sort(arr):
    a = arr.copy()
    steps = []
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
            # Push state after every comparison
            steps.append({
                "array": a.copy(),
                "comparing": [j, j + 1],
                "sorted": list(range(n - i, n))
            })
    return steps

def selection_sort(arr):
    a = arr.copy()
    steps = []
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if a[j] < a[min_idx]:
                min_idx = j
            # Push state for comparison
            steps.append({
                "array": a.copy(),
                "comparing": [min_idx, j],
                "sorted": list(range(i))
            })
        a[i], a[min_idx] = a[min_idx], a[i]
        # Push state after swap
        steps.append({
            "array": a.copy(),
            "swapping": [i, min_idx],
            "sorted": list(range(i + 1))
        })
    return steps

def insertion_sort(arr):
    a = arr.copy()
    steps = []
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and key < a[j]:
            a[j + 1] = a[j]
            j -= 1
            steps.append({
                "array": a.copy(),
                "comparing": [j + 1, i], # Show what's being compared/shifted
                "sorted": list(range(i))
            })
        a[j + 1] = key
        steps.append({
            "array": a.copy(),
            "swapping": [j + 1], # Show where the key is inserted
            "sorted": list(range(i + 1))
        })
    return steps

def merge_sort(arr):
    # This one is more complex to visualize step-by-step, so we'll simplify
    # We'll just show the array getting progressively sorted.
    steps = []
    a = arr.copy()

    def merge_sort_recursive(a):
        if len(a) > 1:
            mid = len(a) // 2
            left = a[:mid]
            right = a[mid:]

            merge_sort_recursive(left)
            merge_sort_recursive(right)

            i = j = k = 0
            while i < len(left) and j < len(right):
                if left[i] < right[j]:
                    a[k] = left[i]
                    i += 1
                else:
                    a[k] = right[j]
                    j += 1
                k += 1
            
            while i < len(left):
                a[k] = left[i]
                i += 1
                k += 1

            while j < len(right):
                a[k] = right[j]
                j += 1
                k += 1
            steps.append({"array": a.copy(), "sorted": []}) # Add a step after each merge

    merge_sort_recursive(a)
    # The final array is fully sorted
    final_steps = []
    for i, step_array in enumerate(steps):
        final_steps.append({
            "array": step_array["array"],
            "sorted": list(range(len(step_array["array"])))
        })
    return final_steps

def quick_sort(arr):
    a = arr.copy()
    steps = []

    def quick_sort_recursive(low, high):
        if low < high:
            pi = partition(low, high)
            quick_sort_recursive(low, pi - 1)
            quick_sort_recursive(pi + 1, high)

    def partition(low, high):
        pivot = a[high]
        i = low - 1
        for j in range(low, high):
            steps.append({
                "array": a.copy(),
                "comparing": [j, high], # Compare with pivot
                "sorted": []
            })
            if a[j] < pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
                steps.append({
                    "array": a.copy(),
                    "swapping": [i, j],
                    "sorted": []
                })
        a[i + 1], a[high] = a[high], a[i + 1]
        steps.append({
            "array": a.copy(),
            "swapping": [i + 1, high],
            "sorted": []
        })
        return i + 1

    quick_sort_recursive(0, len(a) - 1)
    # Mark all as sorted at the end
    final_step = {"array": a.copy(), "sorted": list(range(len(a)))}
    steps.append(final_step)
    return steps

def heap_sort(arr):
    a = arr.copy()
    n = len(a)
    steps = []

    def heapify(n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        if l < n and a[l] > a[largest]:
            largest = l
        if r < n and a[r] > a[largest]:
            largest = r
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            steps.append({
                "array": a.copy(),
                "swapping": [i, largest],
                "sorted": []
            })
            heapify(n, largest)

    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)
    
    # Extract elements one by one
    for i in range(n - 1, 0, -1):
        a[i], a[0] = a[0], a[i]
        steps.append({
            "array": a.copy(),
            "swapping": [0, i],
            "sorted": list(range(i, n))
        })
        heapify(i, 0)
    
    steps.append({"array": a.copy(), "sorted": list(range(n))})
    return steps

def radix_sort(arr):
    a = arr.copy()
    steps = []
    max_val = max(a) if a else 0
    exp = 1
    n = len(a)
    
    while max_val // exp > 0:
        # Counting sort based on digit at exp
        output = [0] * n
        count = [0] * 10
        
        for i in range(n):
            index = (a[i] // exp) % 10
            count[index] += 1
        
        for i in range(1, 10):
            count[i] += count[i - 1]
        
        i = n - 1
        while i >= 0:
            index = (a[i] // exp) % 10
            output[count[index] - 1] = a[i]
            count[index] -= 1
            i -= 1
            
        for i in range(n):
            a[i] = output[i]
        
        steps.append({"array": a.copy(), "sorted": []})
        exp *= 10
        
    steps.append({"array": a.copy(), "sorted": list(range(n))})
    return steps

# --- Search Algorithm ---

def binary_search(arr, target):
    # Binary search requires a sorted array. The frontend should ensure this.
    a = arr.copy()
    low, high = 0, len(a) - 1
    steps = []
    
    while low <= high:
        mid = (low + high) // 2
        steps.append({
            "low": low,
            "high": high,
            "mid": mid,
            "found": False
        })
        
        if a[mid] == target:
            steps[-1]["found"] = True
            return steps
        elif a[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
            
    return steps # Return steps even if not found

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sort', methods=['POST'])
def sort_api():
    data = request.json
    array = data.get("array", [])
    algorithm = data.get("algorithm", "bubble")
    
    # Map algorithm name to function
    algos = {
        "bubble": bubble_sort,
        "selection": selection_sort,
        "insertion": insertion_sort,
        "merge": merge_sort,
        "quick": quick_sort,
        "heap": heap_sort,
        "radix": radix_sort
    }
    
    if algorithm in algos:
        steps = algos[algorithm](array)
        return jsonify({"steps": steps})
    else:
        return jsonify({"error": "Algorithm not implemented"}), 400

@app.route('/api/search', methods=['POST'])
def search_api():
    data = request.json
    array = data.get("array", [])
    target = data.get("target", None)
    
    if target is None:
        return jsonify({"error": "Target value not provided"}), 400
        
    # IMPORTANT: Binary search requires a sorted array.
    # We sort it first to ensure correctness, but this means the visualization
    # will start on a sorted array.
    sorted_array = sorted(array)
    steps = binary_search(sorted_array, target)
    
    return jsonify({
        "steps": steps,
        "sorted_array": sorted_array # Send back the sorted version for visualization
    })

if __name__ == "__main__":
    app.run(debug=True)
