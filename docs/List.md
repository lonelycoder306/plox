## About List Objects
* Relying on Python's built-in ```list``` class/type, the List (capital-L) objects in this implementation are heterogeneous (i.e., they can hold objects of different types), variable-length (i.e., can expand automatically to hold any number of elements) arrays.
* Lists can not only hold regular objects, such as number or Booleans, but rather any first-class object, such as a class or class instance, a function, a lambda, or even another list.

## Constructing List Objects
* To *declare* a list object, you must use the ```list``` modifier:\
    ```list a;```
* Though it may be changed later (since Lox is dynamically-typed), an initializer in a list definition *must* be a List object.
  * Both of these will result in an error:
    ```
    list a = 1; // Error! Cannot initialize a list with a non-list object.
    var a = [1,2,3]; // Error! Cannot use the 'var' modifier to declare a list.
    ```
* An initializer for a list object can be one of four things:
    1. A list literal: ```[..., ..., ...]```.\
       Note: Lambdas can be declared within a list literal.\
       Examples:
       ```
       list a = [1,2,3];
       list b = [fun (x) {print x;}];
       list c = [1, true, "Hello, world!"];
       ```
    2. Another List object.\
       For example:
       ```
       list a = [1,2,3];
       list b = a;
       ```
    3. The ```List()``` constructor.\
       The constructor can accept five arguments:
       * No argument &rarr; The constructor will return an empty List object.
       * A list literal &rarr; The constructor will return a List object containing the same elements as the passed list.
       * A List object &rarr; The constructor will return a **copy** of the passed List object.
       * A string &rarr; The constructor will return a list where each character of the string is a separate element.
       * An integer &rarr; The constructor will return a list containing that number of elements, all initialized to ```nil```.\
         Examples:
         ```
         list a = List(); // a = []
         list b = List([1,2,3]); // b = [1,2,3]
         list c = List(a); // c = []
         list d = List("string"); // d = ["s", "t", "r", "i", "n", "g"]
         list e = List(5); // e = [nil, nil, nil, nil, nil]
         ```
    4. A function call to the built-in ```reference()``` function.
       * This function can accept a List object as its argument, returning that object itself (*not* a copy of it).
       * A call to this function cannot itself be treated as a List object. For example, the following is not allowed:
         ```
         list a = [1,2,3];
         reference(a) = [1,2,3,4]; // Error! Can't treat reference(a) as an lvalue List object.
         reference(a).add(4); // Repeated error.
         ```

## List Methods
Below are all the methods that may be called on a List object, including their parameters and output.

### add(element)
* Appends the given element to the list.

### insert(index, element)
* Inserts the given element at the given index in the List instance.\
**Note:**
  * If the index is larger than the number of elements in the list, the element is appended to the end.
  * Negative indices wrap around (-1 places the element before the previous last element, just as 0 places the element before the previous first element).

### pop()
* Pops the last element in the list and returns it.\
**Note:** if the list is empty, it does nothing and returns ```nil```.

### remove(index)
* Removes the element at the specified index and returns it.
* Will raise an error if the index is negative or beyond the end of the list.

### delete(element, all = false)
* If ```all``` is set to ```true```, removes all occurrences of the given element in the list.\
* If ```all``` is set to ```false``` (or left with its default value), only removes the first occurrence of the given element in the list.\
* Does nothing if the element is not present in the list.

### join()
* Takes a list of strings and returns a string of all the elements concatenated (in order).
* Raises an error if any element in the list isn't a string.

### unique()
* Returns a new list containing the elements of the original with any duplicates removed.

### forEach(operation)
* Executes the given operation (any callable object) on each element of the list.

### transform(mapping)
* Maps each element in the list to a new element according to the ```mapping``` argument (any callable, value-returning object).
* Returns a list with the mapped-to values (in the same order as the original list).

### filter(condition)
* Returns a list with only the elements that satisfy the given condition (any callable, Boolean-returning object).

### flat()
* Returns a flattened version of the list (any inner lists are swapped with the elements within them recursively).
* Example: [[1,2], 3, [[4], 5]] &rarr; [1,2,3,4,5].

### contains(element)
* Returns ```true``` if the element is within the list, and ```false``` otherwise.

### duplicate()
* Returns ```true``` if the list contains duplicates, and ```false``` if it does not.

### index(element)
* Returns the index of the *first* occurrence of the given element in the list.
* Returns ```nil``` if the element is not found within the list.

### indexLast(element)
* Returns the index of the *last* occurrence of the given element in the list.
* Returns ```nil``` if the element is not found within the list.

### any(condition)
* Returns ```true``` if *any* element in the list satisifies the given condition (any callable, Boolean-returning object), and returns ```false``` otherwise.

### all(condition)
* Returns ```true``` if *all* elements in the list satisify the given condition (any callable, Boolean-returning object), and returns ```false``` otherwise.

### reverse()
* Returns a new list that is the reverse of the original.

### sort(ascending = true)
* Sorts a list containing numbers or containing strings (no other list types are permitted).
* Returns the new, sorted list.
* Numbers are sorted by numeric value, while strings are sorted by ASCII value comparison.
* If ```ascending``` is set to/left as ```true```, the new list is sorted in ascending order.
* If ```ascending``` is set to ```false```, the new list is sorted in descending order.

### sorted(ascending = true)
* Returns whether or not the list is currently in order.
* If ```ascending``` is set to/left as ```true```, it returns whether or not the list is in ascending order.
* If ```ascending``` is set to ```false```, it returns whether or not the list is in descending order.

### pair(secondList)
* Constructs a new list which contains list objects, each holding matched pairs from the current list and the argument.
* Example:
  ```
  list a = [1,2,3];
  list b = [2,4,6];
  list c = a.pair(b); // c = [[1, 2], [2, 4], [3, 6]]
  ```
* Will continue constructing pairs until the end is reached for either list.
* Example:
  ```
  list a = [1,2,3];
  list b = [2,4,6,8,10];
  list c = a.pair(b); // c = [[1, 2], [2, 4], [3, 6]]
  ```

### separate()
* Takes a paired list like that constructed with ```pair()``` and constructs a new list containing the original pair of lists used to form it.
* Example:
  ```
  list a = [1,2,3];
  list b = [2,4,6];
  list c = a.pair(b); // c = [[1, 2], [2, 4], [3, 6]]
  list d = c.separate(); // d = [[1, 2, 3], [2, 4, 6]]
  ```

### sum()
* Returns the sum of the elements in the list.
* Only accepts lists with purely numeric elements.

### min()
* Returns the minimum value in the list.
* Only accepts lists with purely numeric elements.

### max()
* Returns the maximum value in the list.
* Only accepts lists with purely numeric elements.

### average()
* Returns the average of all the values in the list.
* Only accepts lists with purely numeric elements.