 
// define PY_ARRAY_UNIQUE_SYMBOL (required by the numpy C-API)
#define PY_ARRAY_UNIQUE_SYMBOL my_module_PyArray_API

// include the vigranumpy C++ API
#include <Python.h>
#include <boost/python.hpp>
#include <vigra/numpy_array.hxx>
#include <vigra/numpy_array_converters.hxx>


typedef vigra::TinyVector<vigra::MultiArrayIndex, 3> TinyVec;

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

template <class T>
struct TemplatedClass
{
    TemplatedClass(T val)
    {
        std::cout << std::endl << val << std::endl;
    }
};


struct TMClass
{
    TMClass() {}
    virtual ~TMClass() {}
    
    template <class T>
    T foo(T in) 
    {
        return 2*in;
    }
};





using namespace boost::python;

template <class T>
void exportTemplatedClass()
{
    class_< TemplatedClass<T> >("TemplatedClass",
        init<T>())
    ;
}


template <class T>
void exportTMClass() 
{
    class_< TMClass >("TMClass",
                      init<>())
    .def("foo", &TMClass::foo<T>, arg("arg1"))
    ;
}

template <class T, class T2, class... Classes>
void exportTMClass()
{
    class_< TMClass >("TMClass",
                      init<>())
    .def("foo", &TMClass::foo<T>, arg("arg1"))
    ;
    exportTMClass<T2, Classes...>();
}


class Unrelated {};


template <class T>
class Base
{
public:
    Base() : val(0) {}
    virtual ~Base() {};
    
    virtual void foo(T val) 
    {
        this->val = val;
    }
    
    T bar() const
    {
        return this->val;
    }
    
protected:
    T val;
};

template <>
class Base<Unrelated&>
{
public:
    
    virtual void foo(Unrelated val) 
    {
        std::cout << "*** Templated: an Unrelated object" << std::endl;
    }
};

template <class... Args> class Interim;

template <class T>
class Interim<T> : public Base<T>
{
public:
    //virtual void foo(T val);
};

template <class T, class... TRest>
class Interim<T, TRest...> : public Interim<TRest...>, public Base<T>
{
public:
    //virtual void foo(T val);
};

class Child : public Interim<int, float>
{
    //using Base<int>::foo;
};

void speak(const Base<int>& bla)
{
    std::cout << "Encountered INT " << bla.bar() << std::endl;
}

void speak(const Base<float>& bla)
{
    std::cout << "Encountered FLOAT " << bla.bar() << std::endl;
}

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

    exportTemplatedClass<int>();
    exportTemplatedClass<float>();
    //exportTMClass<int>();
    //exportTMClass<float>();
    exportTMClass<int, float>();
    
    Child c;
    Unrelated u;
    
    c.Base<int>::foo(1);
    c.Base<float>::foo(.5);
    
    speak((Base<int>)c);
    speak((Base<float>)c);
    //c.foo(u);
}
