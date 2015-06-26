# Django Node Test

Test your JavaScript client against your Django application without adding a single template.

    class FooTest(NodeTestCase):
        def test_create_foo(self):
            data = self.run_test_script('tests/test-create-foo.js')
            self.assertTrue(Foo.objects.exists())


# Requirements

NodeJS


# Why?

Writing unit tests for JavaScript is easy, and writing unit tests for Django is easy, but writing integration tests or simply
testing your JavaScript client against your Django app is not as straight forward (especially if you are writing the html last, or not at all).

This makes it possible to develop your JavaScript client and your Django app in parallel without writing a single line of HTML.

Imagine that you are writing a JavaScript client that talks to your Django app via REST services.
It is not necessarily easy to test the JavaScript against the API.
There are headless browsers, like PhantomJS but that requires a url and a template to load the test script, and if you want to
test different parts of your script then this becomes even more involved.


## Setup

1.  `pip install nodetest`
2.  set `NODETEST_SCRIPT_ROOT` in settings to point to the root of your JavaScript files (e.g: `join(BASE_DIR, 'static', 'js')`)


## Configuration (settings.py)

Optional settings:

    NODETEST_NODE_BIN  # Defaults to `node`, but handy if you want to run babel-node or such

Required settings:

    NODETEST_SCRIPT_ROOT # e.g NODETEST_SCRIPT_ROOT = join(BASE_DIR, 'static', 'js')


## Making requests

Since the code is run by Node and not in a browser, some functions and classes are unavailable.
`XMLHttpRequest` is one of them. 

To solve this run `npm install xmlhttprequest --save-dev`.
Put `global.XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;` at the top of your test
to make `XMLHttpRequest` globally available (like it is in a browser)


## Bootstrapping your tests (not required, but handy)

Adding a `bootstrap.js` can be handy to import code onto the global space.
E.g make the XMLHttpRequest available for all tests create a file named `bootstrap.js` (or any other suitable name), and
add `global.XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;`.

When creating a new test case put `require("./bootstrap");` at the top of the file and all the global variables
will be available.


## An example test case

Create a directory for your tests (e.g "integration_tests").
Add a new test JavaScript test case (e.g "a-test-case.js").

The following code will make a request to http://echo.jsontest.com/foo/bar, which will return the JSON data `{"foo": "bar"}`:

    global.XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest
    
    var req = new XMLHttpRequest();
    req.open("get", "http://echo.jsontest.com/foo/bar");
    req.setRequestHeader("Content-Type", "application/json");

    req.onreadystatechange = function () {
        if (req.status >= 200 && req.status <= 299) {
            console.log(req.responseText);
        }
    };
    req.send();
    


With the script file "integration_tests/a-test-case.js" it's now possible to create the Django test case:
    

    from django.contrib.auth import get_user_model
    from nodetest.test_case import NodeTestCase
    
    
    class UserTest(NodeTestCase):
        def test_sign_in(self):
            data = self.run_test_script('integration_tests/a-test-case.js')
            self.assertEqual(data['foo'], 'bar')


## What is NodeTestCase and what does it do

`NodeTestCase` is extending `LiveServerTestCase`. 
This makes it possible to test your REST api against your Python code.

By default `LiveServerTestCase` starts a dev server available at "http://localhost:8081".

This makes it possible to test your JavaScript client against your Django app (this is particularly handy to use with Django Rest Framework)
by writing tests for the JavaScript client directly without loading a headless browser or even writing a single line of HTML at all.


### `run_test_script(...)`

`run_test_script` takes three arguments and returns a dictionary (or plain text):

*  `script_file`
*  `plaintext` (default is False)
*  `enable_console` (default is False)


#### `script_file`

This is the relative path to your script file.
Joined with `settings.NODETEST_SCRIPT_ROOT` it should make an absolute path to the location of the script.


#### `plaintext`

If `plaintext` is True, all output from `console.log` in your JavaScript file will be added to the return value
of `self.run_test_script`.

By default it will parse and return JSON.


#### `enable_console`

If `enable_console` is set to True anything written to stdout (e.g console.log statements) in your test will be output to the terminal (like a print statement), 
otherwise it will be collected and returned by  `run_test_script`.


## Important note about `console.log` in your script file

`console.log` is used to output data from JavaScript. Every time `console.log` is used the output will be added to the return value
of `run_test_script`.
 
By default `run_test_script` assumes a dictionary is being returned (this can be changed by passing `plaintext=True` to `run_test_script`)
by parsing the output from the script.

By adding this line in your test script (or put it in your "bootstrap.js" file):

    global.outputJson = function(str) { console.log(JSON.stringify(str)); }
 
it becomes obvious that you want to return JSON to your `NodeTestCase`.
However if you call `console.log` multiple times it will most likely mangle the output.
Therefore you should either:

**Only call `console.log` once in your test**

or

**set `plain_text=True` in your `run_test_script` call**
