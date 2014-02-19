#include <boost/python.hpp>


/* pure c++ */

class Mighty
{
public:
    Mighty() {}
    virtual ~Mighty() {}
    virtual int canswer() {return 42;}
    virtual int answer() = 0;
};

class God
{
public:
    God() {};
    virtual ~God() {};
    virtual int answer() {return smite();}
    virtual int smite() = 0;
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
        return Mighty::canswer();
    }

    int default_answer()
    {
        return this->Mighty::canswer();
    }
};

class GodWrap : public God, public wrapper<God>
{
public:
    int smite()
    {
        return this->get_override("smite")();
    }
};


BOOST_PYTHON_MODULE(libmytest)
{
    def("yay", yay);
    def("mycall", mycall, args("mighty"));

    
    class_<MightyWrap, boost::noncopyable>("Mighty")
        .def("answer", &Mighty::answer, &MightyWrap::default_answer)
        ;
    

    class_<GodWrap, bases<Mighty>, boost::noncopyable>("God")
        .def("answer", pure_virtual(&God::smite));
        ;

}
