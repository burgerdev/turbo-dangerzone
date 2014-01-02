#include <boost/python.hpp>


/* pure c++ */

class Mighty
{
public:
    Mighty() {}
    virtual ~Mighty() {}
    virtual int answer() {return 42;}
};

char const* yay()
{
  return "Yay!";
}

int mycall(Mighty &mighty)
{
    return mighty.answer();
}

/* Python interface */
using namespace boost::python;

struct MightyWrap : Mighty, wrapper<Mighty>
{
public:
    int answer()
    {
        if (override foo = this->get_override("answer"))
            return foo();
        return Mighty::answer();
    }

    int default_answer()
    {
        return this->Mighty::answer();
    }
};


BOOST_PYTHON_MODULE(libmytest)
{
    def("yay", yay);
    def("mycall", mycall, args("mighty"));

    class_<MightyWrap, boost::noncopyable>("Mighty")
        .def("answer", &Mighty::answer, &MightyWrap::default_answer)
        ;
}
