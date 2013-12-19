#include <boost/python/class.hpp>
#include <boost/python/module_init.hpp>
#include <boost/python/def.hpp>
#include <boost/python/call_method.hpp>
#include <boost/ref.hpp>
#include <boost/utility.hpp>

using namespace boost::python;

struct baz {
    virtual int pure(int) = 0;
    int calls_pure(int x) { return pure(x) + 1000; }
};

struct baz_callback : baz {
    baz_callback(PyObject *p) : self(p) {}
    int pure(int x) { return call_method<int>(self, "pure", x); }
    PyObject *self;
};

BOOST_PYTHON_MODULE_INIT(foobar)
{
     class_<baz, boost::noncopyable, boost::shared_ptr<baz_callback> >("baz")
         .def("calls_pure", &baz::calls_pure);
}
