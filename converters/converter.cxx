 
// define PY_ARRAY_UNIQUE_SYMBOL (required by the numpy C-API)
#define PY_ARRAY_UNIQUE_SYMBOL my_module_PyArray_API

// include the vigranumpy C++ API
#include <Python.h>
#include <boost/python.hpp>
#include <vigra/numpy_array.hxx>
#include <vigra/numpy_array_converters.hxx>


typedef vigra::TinyVector<int, 3> TinyVec;

struct Convert_to_python
{
    Convert_to_python()
    {
        boost::python::converter::registry::push_back(
            &convertible,
            &construct,
            boost::python::type_id<TinyVec>());
    }
 
    // Determine if obj_ptr can be converted in a QString
    static void* convertible(PyObject* obj_ptr)
    {
        if (!PyTuple_Check(obj_ptr)) return 0;
        if (PyTuple_Size(obj_ptr) != 3) return 0;
        
        return obj_ptr;
    }
 
    // Convert obj_ptr into a QString
    static void construct(
    PyObject* obj_ptr,
    boost::python::converter::rvalue_from_python_stage1_data* data)
    {
 
        // Grab pointer to memory into which to construct the new QString
        void* storage = (
        (boost::python::converter::rvalue_from_python_storage<TinyVec>*)
        data)->storage.bytes;

        // in-place construct the new QString using the character data
        // extraced from the python object
        
        
        new (storage) TinyVec(0, 0, 0);

        // Stash the memory chunk pointer for later use by boost.python
        data->convertible = storage;
    }
};



struct MyClass
{
    void foo(int arg1, int arg2)
    {
        std::cout << "Args:" << std::endl;
        std::cout << arg1 << ", " << arg2 << std::endl;
    }
    
    
    void baz(TinyVec vec)
    {
        std::cout << "Args:" << std::endl;
        for (int i=0; i<3; i++)
            std::cout << vec[i] << ((i<2) ? ", " : "");
        std::cout << std::endl;
    }
};

struct MyOtherClass
{
    MyOtherClass(TinyVec vec)
    {
        std::cout << "Args:" << std::endl;
        for (int i=0; i<3; i++)
            std::cout << vec[i] << ((i<2) ? ", " : "");
        std::cout << std::endl;
    }
    
    
};


using namespace boost::python;

// the argument of the init macro must be the module name
BOOST_PYTHON_MODULE_INIT(converter)
{
    using namespace boost::python;
    
    // initialize numpy and vigranumpy
    vigra::import_vigranumpy();
    
    //Convert_to_python();

    // export a class and its member functions
    class_<MyClass>("MyClass",
        "Documentation (currently unavailable)")
        .def("foo", &MyClass::foo,
             (arg("arg1"), arg("arg2")),
             "Documentation")
        .def("baz", &MyClass::baz,
             (arg("vec")))
    ;
    
    class_<MyOtherClass>("MyOtherClass",
        init<TinyVec>())
    ;

}
