## About List Objects
* Relying on Python's built-in ```list``` class/type, the List (capital-L) objects in this implementation are heterogeneous (i.e., they can hold objects of different types), variable-length (i.e., can expand automatically to hold any number of elements) arrays.
* Lists can not only hold regular objects, such as number or Booleans, but rather any first-class object, such as a class or class instance, a function, a lambda, or even another list.

## Constructing List Objects
* To *declare* a list object, you must use the ```list``` modifier:\
    ```list a;```
* Though it may be changed later (since Lox is dynamically-typed), an initializer in a list definition *must* be a List object.
  * Both of these will result in an error:
    ```
    list a = 1;
    var a = [1,2,3];
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
         list a = List();
         list b = List([1,2,3]);
         list c = List(a);
         list d = List("string");
         list e = List(5);
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
Appends the given element to the List instance.

### insert(index, element)
Inserts the given element at the given index in the List instance.\
**Note:**
* If the index is larger than the number of elements in the list, the element is appended to the end.
* Negative indices wrap around (-1 places the element before the previous last element, just as 0 places the element before the previous first element).

### pop()
Pops the last element in the list and returns it.\
**Note:** if the list is empty, it does nothing and returns ```nil```.

### remove(index)
...

### delete(element, all = false)
If all is set to true, removes all occurrences of the given element in the list.\
If all is set to false (or left with its default value), only removes the first occurrence of the given element in the list.\
Does nothing if the element is not present in the list.
