
#include <iostream>
#include <sstream>
#include <map>
#include <set>

#include <vigra/impex.hxx>

#include <vigra/multi_array.hxx>
#include <vigra/numpy_array.hxx>
#include <vigra/accumulator.hxx>
#include <vigra/unittest.hxx>

#include <sys/resource.h>

#include "pythonaccumulator.hxx"

using namespace vigra;

template <class TAG, class A>
static inline typename acc::LookupDependency<TAG, A>::reference
getAccumulatorIndirectly(A & a)
{
    typedef typename acc::LookupDependency<TAG, A>::Tag StandardizedTag;
    typedef typename acc::LookupDependency<TAG, A>::reference reference;
    return acc::acc_detail::CastImpl<StandardizedTag, typename A::Tag, reference>::exec(a);
}

void testRegionAccumulators()
{
    using namespace vigra::acc;
    {
        typedef CoupledIteratorType<2, int>::type Iterator;
        typedef Iterator::value_type Handle;
        typedef Shape2 V;

        typedef Select<Count, RegionAnchor, Coord<Sum>, Global<Count>, Global<Coord<Minimum> >, LabelArg<1>, DataArg<1> > Selected;
        typedef AccumulatorChainArray<Handle, Selected> A;

        should((IsSameType<acc::acc_detail::ConfigureAccumulatorChainArray<Handle, Selected>::GlobalTags, 
                            TypeList<Count,TypeList<Coord<Minimum>,TypeList<DataArg<1>, TypeList<LabelArg<1>, void> > > > >::value));
        should((IsSameType<acc::acc_detail::ConfigureAccumulatorChainArray<Handle, Selected>::RegionTags, 
                            TypeList<RegionAnchor,TypeList<Count,TypeList<Coord<Sum>,TypeList<DataArg<1>, TypeList<LabelArg<1>, void> > > > > >::value));

        typedef LookupTag<Count, A>::type RegionCount;
        typedef LookupDependency<Global<Count>, RegionCount>::type GlobalCountViaRegionCount;

        should(!(IsSameType<RegionCount, LookupTag<Global<Count>, A>::type>::value));
        should((IsSameType<GlobalCountViaRegionCount, LookupTag<Global<Count>, A>::type>::value));

        MultiArray<2, int> labels(Shape2(3,2));
        labels(2,0) = labels(2,1) = 1;
        Iterator i     = createCoupledIterator(labels),
                    start = i,   
                    end   = i.getEndIterator();

        A a;

        shouldEqual(1, a.passesRequired());

        a.setMaxRegionLabel(1);

        shouldEqual(a.maxRegionLabel(), 1);
        shouldEqual(a.regionCount(), 2);
        should((&getAccumulator<Count, A>(a, 0) != &getAccumulator<Count, A>(a, 1)));

        LookupTag<Count, A>::reference rc = getAccumulator<Count>(a, 0);
        LookupTag<Global<Count>, A>::reference gc = getAccumulator<Global<Count> >(a);
        should((&gc == &getAccumulatorIndirectly<Global<Count> >(rc)));
        should((&gc == &getAccumulatorIndirectly<Global<Count> >(getAccumulator<Count>(a, 1))));

        for(; i < end; ++i)
            a(*i);
        
        shouldEqual(4, get<Count>(a, 0));
        shouldEqual(2, get<Count>(a, 1));
        shouldEqual(6, get<Global<Count> >(a));

        shouldEqual(Shape2(0,0), get<RegionAnchor>(a, 0));
        shouldEqual(Shape2(2,0), get<RegionAnchor>(a, 1));

        shouldEqual(V(2,2), get<Coord<Sum> >(a, 0));
        shouldEqual(V(4,1), get<Coord<Sum> >(a, 1));
        shouldEqual(V(0,0), get<Global<Coord<Minimum> > >(a));

        a.merge(1, 0);

        shouldEqual(6, get<Count>(a, 1));
        shouldEqual(Shape2(0,0), get<RegionAnchor>(a, 1));
        shouldEqual(V(6,3), get<Coord<Sum> >(a, 1));

        A aa;
        aa.setMaxRegionLabel(1);
        aa.setCoordinateOffset(V(2, -1));

        for(i = start; i < end; ++i)
            aa(*i);
        
        shouldEqual(4, get<Count>(aa, 0));
        shouldEqual(2, get<Count>(aa, 1));
        shouldEqual(6, get<Global<Count> >(aa));

        shouldEqual(V(10,-2), get<Coord<Sum> >(aa, 0));
        shouldEqual(V(8,-1), get<Coord<Sum> >(aa, 1));
        shouldEqual(V(2,-1), get<Global<Coord<Minimum> > >(aa));

        A ab;
        ab.setMaxRegionLabel(1);
        ab.setCoordinateOffset(V(2, -1));
        ab.setCoordinateOffset(0, V(-1,1));
        ab.setCoordinateOffset(1, V(1,-2));

        for(i = start; i < end; ++i)
            ab(*i);
        
        shouldEqual(4, get<Count>(ab, 0));
        shouldEqual(2, get<Count>(ab, 1));
        shouldEqual(6, get<Global<Count> >(ab));

        shouldEqual(V(-2,6), get<Coord<Sum> >(ab, 0));
        shouldEqual(V(6,-3), get<Coord<Sum> >(ab, 1));
        shouldEqual(V(2,-1), get<Global<Coord<Minimum> > >(ab));

        A b;
        b.ignoreLabel(0);

        i = start;

        for(; i < end; ++i)
            b(*i);
        
        shouldEqual(0, get<Count>(b, 0));
        shouldEqual(2, get<Count>(b, 1));
        shouldEqual(2, get<Global<Count> >(b));

        shouldEqual(V(0,0), get<Coord<Sum> >(b, 0));
        shouldEqual(V(4,1), get<Coord<Sum> >(b, 1));
        shouldEqual(V(2,0), get<Global<Coord<Minimum> > >(b));
    }

    {
        typedef CoupledIteratorType<2, double, int>::type Iterator;
        typedef Iterator::value_type Handle;

        typedef AccumulatorChainArray<Handle, Select<Count, RegionPerimeter, RegionCircularity, RegionEccentricity, 
                                                        AutoRangeHistogram<3>, GlobalRangeHistogram<3>,
                                                        Global<Count>, Global<AutoRangeHistogram<3> >, DataArg<1>, LabelArg<2>
                                        > > A;

        double d[] = { 1.0, 3.0, 3.0,
                        1.0, 2.0, 5.0 };
        MultiArrayView<2, double> data(Shape2(3,2), d);

        MultiArray<2, int> labels(Shape2(3,2));
        labels(2,0) = labels(2,1) = 1;

        Iterator i     = createCoupledIterator(data, labels),
                    start = i,   
                    end   = i.getEndIterator();

        A a;
        shouldEqual(a.regionCount(), 0);
        shouldEqual(2, a.passesRequired());

        for(; i < end; ++i)
            a(*i);
        
        shouldEqual(a.maxRegionLabel(), 1);
        shouldEqual(a.regionCount(), 2);
        shouldEqual(4, get<Count>(a, 0));
        shouldEqual(2, get<Count>(a, 1));
        shouldEqual(6, get<Global<Count> >(a));

        shouldEqual(1, get<Minimum>(a, 0));
        shouldEqual(3, get<Minimum>(a, 1));
        shouldEqual(1, get<Global<Minimum> >(a));

        shouldEqual(3, get<Maximum>(a, 0));
        shouldEqual(5, get<Maximum>(a, 1));
        shouldEqual(5, get<Global<Maximum> >(a));

        for(i = start; i < end; ++i)
            a.updatePass2(*i);
        
        shouldEqual(4, get<Count>(a, 0));
        shouldEqual(2, get<Count>(a, 1));
        shouldEqual(6, get<Global<Count> >(a));

        typedef TinyVector<double, 3> V;

        shouldEqual(V(2,1,1), get<AutoRangeHistogram<3> >(a, 0));
        shouldEqual(V(1,0,1), get<AutoRangeHistogram<3> >(a, 1));
        shouldEqual(V(3,1,0), get<GlobalRangeHistogram<3> >(a, 0));
        shouldEqual(V(0,1,1), get<GlobalRangeHistogram<3> >(a, 1));
        shouldEqual(V(3,2,1), get<Global<AutoRangeHistogram<3> > >(a));

        typedef LookupTag<RegionContour, A>::value_type::value_type Point;

        Point ref0[] = { Point(0, -0.5), Point(-0.5, 0), Point(-0.5, 1), Point(0, 1.5), Point(1, 1.5), 
                            Point(1.5, 1), Point(1.5, 0), Point(1, -0.5), Point(0.0, -0.5) };
        shouldEqual(get<RegionContour>(a, 0).size(), 9);
        shouldEqualSequence(get<RegionContour>(a, 0).cbegin(), get<RegionContour>(a, 0).cend(), ref0);
        shouldEqualTolerance(get<RegionPerimeter>(a, 0), 4.0 + 2.0*M_SQRT2, 1e-15);
        shouldEqualTolerance(get<RegionCircularity>(a, 0), 0.9712214720608953, 1e-15);
        shouldEqualTolerance(get<RegionEccentricity>(a, 0), 0.0, 1e-15);

        Point ref1[] = { Point(2, -0.5), Point(1.5, 0), Point(1.5, 1), Point(2, 1.5), 
                            Point(2.5, 1), Point(2.5, 0), Point(2, -0.5) };
        shouldEqual(get<RegionContour>(a, 1).size(), 7);
        shouldEqualSequence(get<RegionContour>(a, 1).cbegin(), get<RegionContour>(a, 1).cend(), ref1);
        shouldEqualTolerance(get<RegionPerimeter>(a, 1), 2.0 + 2.0*M_SQRT2, 1e-15);
        shouldEqualTolerance(get<RegionCircularity>(a, 1), 0.8991763601646624, 1e-15);
        shouldEqualTolerance(get<RegionEccentricity>(a, 1), 1.0, 1e-15);
    }

    {
        typedef CoupledIteratorType<2, double, int>::type Iterator;

        typedef DynamicAccumulatorChainArray<CoupledArrays<2, double, int>, 
                                            Select<Count, Coord<Mean>, GlobalRangeHistogram<3>,
                                                    AutoRangeHistogram<3>, 
                                                    Global<Count>, Global<Coord<Mean> >, 
                                                    StandardQuantiles<GlobalRangeHistogram<3> >, 
                                                    LabelArg<2>, DataArg<1>
                                                > > A;

        A a;

        shouldEqual(0, a.passesRequired());

        should(!isActive<Count>(a));
        should(!isActive<Coord<Sum> >(a));
        should(!isActive<GlobalRangeHistogram<3> >(a));

        should(!isActive<Global<Count> >(a));
        should(!isActive<Global<Minimum> >(a));
        should(!isActive<Global<Coord<Sum> > >(a));

        activate<Count>(a);
        should(isActive<Count>(a));
        should(!isActive<Global<Count> >(a));

        //activate<Global<Count> >(a);
        a.activate("Global<PowerSum<0> >");

        should(isActive<Count>(a));
        should(isActive<Global<Count> >(a));

        //activate<Coord<Mean> >(a);
        a.activate("Coord<DivideByCount<PowerSum<1> > >");
        should(isActive<Coord<Mean> >(a));
        should(isActive<Coord<Sum> >(a));
        should(!isActive<Global<Coord<Sum> > >(a));
        should(!isActive<Global<Coord<Mean> > >(a));

        activate<Global<Coord<Mean> > >(a);
        should(isActive<Global<Coord<Sum> > >(a));
        should(isActive<Global<Coord<Mean> > >(a));
        should(!isActive<GlobalRangeHistogram<3> >(a));
        should(!isActive<AutoRangeHistogram<3> >(a));
        should(!isActive<Global<Minimum> >(a));

        shouldEqual(1, a.passesRequired());

        activate<GlobalRangeHistogram<3> >(a);
        a.activate("AutoRangeHistogram<3>");

        should(isActive<GlobalRangeHistogram<3> >(a));
        should(isActive<AutoRangeHistogram<3> >(a));
        should(isActive<Global<Minimum> >(a));

        shouldEqual(2, a.passesRequired());

        MultiArray<2, double> data(Shape2(3,2));
        data(0,0) = 0.1;
        data(2,0) = 1.0;
        data(2,1) = 0.9;
        MultiArray<2, int> labels(Shape2(3,2));
        labels(2,0) = labels(2,1) = 1;
        Iterator i     = createCoupledIterator(data, labels),
                    start = i,   
                    end   = i.getEndIterator();

        for(; i < end; ++i)
            a(*i);
        
        for(i = start; i < end; ++i)
            a.updatePass2(*i);
        
        shouldEqual(a.maxRegionLabel(), 1);
        shouldEqual(4, get<Count>(a, 0));
        shouldEqual(2, get<Count>(a, 1));
        shouldEqual(6, get<Global<Count> >(a));

        typedef TinyVector<double, 2> V;

        shouldEqual(V(0.5, 0.5), get<Coord<Mean> >(a, 0));
        shouldEqual(V(2, 0.5), get<Coord<Mean> >(a, 1));
        shouldEqual(V(1, 0.5), get<Global<Coord<Mean> > >(a));

        should(getAccumulator<GlobalRangeHistogram<3> >(a,0).scale_ == getAccumulator<GlobalRangeHistogram<3> >(a,1).scale_);
        should(getAccumulator<GlobalRangeHistogram<3> >(a,0).scale_ != getAccumulator<AutoRangeHistogram<3> >(a,0).scale_);
        should(getAccumulator<GlobalRangeHistogram<3> >(a,1).scale_ != getAccumulator<AutoRangeHistogram<3> >(a,1).scale_);
        
        typedef TinyVector<double, 3> W;
        shouldEqual(W(4, 0, 0), get<GlobalRangeHistogram<3> >(a,0));
        shouldEqual(W(0, 0, 2), get<GlobalRangeHistogram<3> >(a,1));
        shouldEqual(W(3, 0, 1), get<AutoRangeHistogram<3> >(a,0));
        shouldEqual(W(1, 0, 1), get<AutoRangeHistogram<3> >(a,1));

        A b;
        b.activateAll();

        extractFeatures(data, labels, b);
        
        shouldEqual(W(4, 0, 0), get<GlobalRangeHistogram<3> >(b,0));
        shouldEqual(W(0, 0, 2), get<GlobalRangeHistogram<3> >(b,1));

        a += b;
        
        shouldEqual(a.maxRegionLabel(), 1);
        shouldEqual(8, get<Count>(a, 0));
        shouldEqual(4, get<Count>(a, 1));
        shouldEqual(12, get<Global<Count> >(a));
        shouldEqual(V(0.5, 0.5), get<Coord<Mean> >(a, 0));
        shouldEqual(V(2, 0.5), get<Coord<Mean> >(a, 1));
        shouldEqual(V(1, 0.5), get<Global<Coord<Mean> > >(a));
        shouldEqual(W(8, 0, 0), get<GlobalRangeHistogram<3> >(a,0));
        shouldEqual(W(0, 0, 4), get<GlobalRangeHistogram<3> >(a,1));
        shouldEqual(W(4, 0, 0), get<GlobalRangeHistogram<3> >(b,0));
        shouldEqual(W(0, 0, 2), get<GlobalRangeHistogram<3> >(b,1));

        TinyVector<int, 2> labelMapping(2, 3);
        a.merge(b, labelMapping);
        shouldEqual(a.maxRegionLabel(), 3);
        shouldEqual(8, get<Count>(a, 0));
        shouldEqual(4, get<Count>(a, 1));
        shouldEqual(4, get<Count>(a, 2));
        shouldEqual(2, get<Count>(a, 3));
        shouldEqual(18, get<Global<Count> >(a));
        shouldEqual(V(0.5, 0.5), get<Coord<Mean> >(a, 0));
        shouldEqual(V(2, 0.5), get<Coord<Mean> >(a, 1));
        shouldEqual(V(0.5, 0.5), get<Coord<Mean> >(a, 2));
        shouldEqual(V(2, 0.5), get<Coord<Mean> >(a, 3));
        shouldEqual(V(1, 0.5), get<Global<Coord<Mean> > >(a));

        A c;
        c.activateAll();
        c.setHistogramOptions(HistogramOptions().regionAutoInit());
        extractFeatures(start, end, c);

        shouldEqual(getAccumulator<GlobalRangeHistogram<3> >(c,0).scale_, getAccumulator<AutoRangeHistogram<3> >(c,0).scale_);
        shouldEqual(getAccumulator<GlobalRangeHistogram<3> >(c,1).scale_, getAccumulator<AutoRangeHistogram<3> >(c,1).scale_);
        
        shouldEqual(W(3, 0, 1), get<GlobalRangeHistogram<3> >(c,0));
        shouldEqual(W(1, 0, 1), get<GlobalRangeHistogram<3> >(c,1));
        shouldEqual(W(3, 0, 1), get<AutoRangeHistogram<3> >(c,0));
        shouldEqual(W(1, 0, 1), get<AutoRangeHistogram<3> >(c,1));

        c.merge(c, TinyVector<int, 2>(3, 2));

        shouldEqual(c.maxRegionLabel(), 3);
        shouldEqual(get<Count>(c, 0), 4);
        shouldEqual(get<Count>(c, 1), 2);
        shouldEqual(get<Count>(c, 2), 2);
        shouldEqual(get<Count>(c, 3), 4);
        shouldEqual(get<Global<Count> >(c), 12);

        shouldEqual(W(3, 0, 1), get<AutoRangeHistogram<3> >(c,0));
        shouldEqual(W(1, 0, 1), get<AutoRangeHistogram<3> >(c,1));
        shouldEqual(W(1, 0, 1), get<AutoRangeHistogram<3> >(c,2));
        shouldEqual(W(3, 0, 1), get<AutoRangeHistogram<3> >(c,3));

        c.merge(1, 2);

        shouldEqual(c.maxRegionLabel(), 3);
        shouldEqual(get<Count>(c, 0), 4);
        shouldEqual(get<Count>(c, 1), 4);
        shouldEqual(get<Count>(c, 2), 0);
        shouldEqual(get<Count>(c, 3), 4);
        shouldEqual(get<Global<Count> >(c), 12);

        shouldEqual(W(3, 0, 1), get<AutoRangeHistogram<3> >(c,0));
        shouldEqual(W(2, 0, 2), get<AutoRangeHistogram<3> >(c,1));
        shouldEqual(W(0, 0, 0), get<AutoRangeHistogram<3> >(c,2));
        shouldEqual(W(3, 0, 1), get<AutoRangeHistogram<3> >(c,3));
    }
}

void testHistogram()
{
    static const int SIZE = 30, HSIZE = 10;
    int data[SIZE] = {4, 3, 2, 2, 2, 0, 3, 6, 8, 8, 4, 0, 2, 0, 2, 8, 7, 8, 6, 0, 9, 3, 7, 0, 9, 5, 9, 9, 2, 4};
    // the same sorted:
    // int data[SIZE] = {0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 6, 6, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9};

    using namespace vigra::acc;
    {

        typedef AccumulatorChain<int, Select<StandardQuantiles<UserRangeHistogram<HSIZE> >, StandardQuantiles<AutoRangeHistogram<HSIZE> >,
                                                StandardQuantiles<IntegerHistogram<HSIZE> >, StandardQuantiles<IntegerHistogram<0> >,
                                                DivideByCount<UserRangeHistogram<HSIZE> >, StandardQuantiles<UserRangeHistogram<HSIZE+2> >,
                                                StandardQuantiles<UserRangeHistogram<3> >, StandardQuantiles<IntegerHistogram<HSIZE+2> >
                                > > A;
        A a;

        getAccumulator<UserRangeHistogram<HSIZE> >(a).setMinMax(-0.5, 9.5);
        getAccumulator<UserRangeHistogram<HSIZE+2> >(a).setMinMax(-1.5, 10.5);
        getAccumulator<UserRangeHistogram<3> >(a).setMinMax(-20.0, 30.0);  // all data in one bin
        getAccumulator<IntegerHistogram<0> >(a).setBinCount(HSIZE);

        shouldEqual(HSIZE, get<IntegerHistogram<HSIZE> >(a).size());
        shouldEqual(HSIZE, get<UserRangeHistogram<HSIZE> >(a).size());
        shouldEqual(HSIZE, get<AutoRangeHistogram<HSIZE> >(a).size());
        shouldEqual(HSIZE, get<IntegerHistogram<0> >(a).size());

        for(int k=0; k<SIZE; ++k)
            a(data[k]);

        for(int k=0; k<SIZE; ++k)
            a.updatePass2(data[k]);

        double h[HSIZE] = { 5.0, 0.0, 6.0, 3.0, 3.0, 1.0, 2.0, 2.0, 4.0, 4.0 };

        shouldEqualSequence(h, h+HSIZE, get<IntegerHistogram<HSIZE> >(a).begin());
        shouldEqualSequence(h, h+HSIZE, get<UserRangeHistogram<HSIZE> >(a).begin());
        shouldEqualSequence(h, h+HSIZE, get<AutoRangeHistogram<HSIZE> >(a).begin());
        shouldEqualSequence(h, h+HSIZE, get<IntegerHistogram<0> >(a).begin());

        double density[HSIZE] = { 5.0/30.0, 0.0, 6.0/30.0, 3.0/30.0, 3.0/30.0, 1.0/30.0, 2.0/30.0, 2.0/30.0, 4.0/30.0, 4.0/30.0 };
        shouldEqualSequence(density, density+HSIZE, get<DivideByCount<UserRangeHistogram<HSIZE> > >(a).begin());

        typedef LookupTag<StandardQuantiles<UserRangeHistogram<HSIZE> >, A>::value_type QuantileVector;
        static const int QSIZE = QuantileVector::static_size;
        shouldEqual(QSIZE, 7);

        double quser[QSIZE] = { 0.0, 0.3, 1.9166666666666666, 3.833333333333333, 7.625, 8.625, 9.0 };
        shouldEqualSequenceTolerance(quser, quser+QSIZE, get<StandardQuantiles<UserRangeHistogram<HSIZE> > >(a).begin(), 1e-15);
        shouldEqualSequenceTolerance(quser, quser+QSIZE, get<StandardQuantiles<UserRangeHistogram<HSIZE+2> > >(a).begin(), 1e-15);

        double q_onebin[QSIZE] = { 0.0, 0.9, 2.25, 4.5, 6.75, 8.1, 9.0 };
        shouldEqualSequenceTolerance(q_onebin, q_onebin+QSIZE, get<StandardQuantiles<UserRangeHistogram<3> > >(a).begin(), 1e-14);
        
        double qauto[QSIZE] = { 0.0, 0.54, 2.175, 3.9, 7.3125, 8.325, 9.0 };
        shouldEqualSequenceTolerance(qauto, qauto+QSIZE, get<StandardQuantiles<AutoRangeHistogram<HSIZE> > >(a).begin(), 1e-15);
        
        double qint[QSIZE] = { 0.0, 0.0, 2.0, 4.0, 7.75, 9.0, 9.0 };
        shouldEqualSequence(qint, qint+QSIZE, get<StandardQuantiles<IntegerHistogram<HSIZE> > >(a).begin());
        shouldEqualSequence(qint, qint+QSIZE, get<StandardQuantiles<IntegerHistogram<0> > >(a).begin());

            // repeat test with negated data => quantiles should be negated, but otherwise the same as before
        a.reset();

        getAccumulator<UserRangeHistogram<HSIZE> >(a).setMinMax(-9.5, 0.5);
        getAccumulator<UserRangeHistogram<HSIZE+2> >(a).setMinMax(-10.5, 1.5);
        getAccumulator<UserRangeHistogram<3> >(a).setMinMax(-30.0, 20.0);
        getAccumulator<IntegerHistogram<0> >(a).setBinCount(HSIZE);

        for(int k=0; k<SIZE; ++k)
            a(-data[k]);

        for(int k=0; k<SIZE; ++k)
            a.updatePass2(-data[k]);

        std::reverse(h, h+HSIZE);
        shouldEqualSequence(h, h+HSIZE, get<UserRangeHistogram<HSIZE> >(a).begin());
        shouldEqualSequence(h, h+HSIZE, get<AutoRangeHistogram<HSIZE> >(a).begin());

        double hneg[HSIZE] = { 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 };
        shouldEqualSequence(hneg, hneg+HSIZE, get<IntegerHistogram<HSIZE> >(a).begin());
        shouldEqualSequence(hneg, hneg+HSIZE, get<IntegerHistogram<0> >(a).begin());

        std::reverse(quser, quser+QSIZE);
        shouldEqualSequenceTolerance(quser, quser+QSIZE, (-get<StandardQuantiles<UserRangeHistogram<HSIZE> > >(a)).begin(), 1e-14);
        
        std::reverse(qauto, qauto+QSIZE);
        shouldEqualSequenceTolerance(qauto, qauto+QSIZE, (-get<StandardQuantiles<AutoRangeHistogram<HSIZE> > >(a)).begin(), 1e-14);

            // repeat test with data shifted by one (test behavior of IntegerHistogram with empty bins at the ends)
        a.reset();

        getAccumulator<UserRangeHistogram<HSIZE> >(a).setMinMax(-0.5, 9.5);
        getAccumulator<UserRangeHistogram<HSIZE+2> >(a).setMinMax(-1.5, 10.5);
        getAccumulator<UserRangeHistogram<3> >(a).setMinMax(-20.0, 30.0);  // all data in one bin
        getAccumulator<IntegerHistogram<0> >(a).setBinCount(HSIZE+2);

        for(int k=0; k<SIZE; ++k)
            a(1+data[k]);

        for(int k=0; k<SIZE; ++k)
            a.updatePass2(1+data[k]);

        shouldEqualSequence(qint, qint+QSIZE, (get<StandardQuantiles<IntegerHistogram<HSIZE+2> > >(a)-QuantileVector(1.0)).begin());
        shouldEqualSequence(qint, qint+QSIZE, (get<StandardQuantiles<IntegerHistogram<0> > >(a)-QuantileVector(1.0)).begin());
    }

    {
        typedef AccumulatorChain<int, Select<UserRangeHistogram<0>, AutoRangeHistogram<0>, IntegerHistogram<0>
                                > > A;
        A a;

        a.setHistogramOptions(HistogramOptions().setMinMax(-0.5, 9.5).setBinCount(HSIZE));

        shouldEqual(HSIZE, get<UserRangeHistogram<0> >(a).size());
        shouldEqual(HSIZE, get<AutoRangeHistogram<0> >(a).size());
        shouldEqual(HSIZE, get<IntegerHistogram<0> >(a).size());

        extractFeatures(data, data+SIZE, a);

        double h[HSIZE] = { 5.0, 0.0, 6.0, 3.0, 3.0, 1.0, 2.0, 2.0, 4.0, 4.0 };

        shouldEqualSequence(h, h+HSIZE, get<UserRangeHistogram<0> >(a).begin());
        shouldEqualSequence(h, h+HSIZE, get<AutoRangeHistogram<0> >(a).begin());
        shouldEqualSequence(h, h+HSIZE, get<IntegerHistogram<0> >(a).begin());

        try 
        {
            A b;
            extractFeatures(data, data+SIZE, b);
            failTest("extractFeatures() failed to throw exception");
        }
        catch(ContractViolation & c) 
        {
            std::string expected("\nPrecondition violation!\nUserRangeHistogram::update(): setMinMax(...) has not been called.");
            std::string message(c.what());
            shouldEqual(expected, message.substr(0,expected.size()));
        }

        try 
        {
            A b;
            getAccumulator<UserRangeHistogram<0> >(b).setMinMax(-2.5, 12.5);
            failTest("extractFeatures() failed to throw exception");
        }
        catch(ContractViolation & c) 
        {
            std::string expected("\nPrecondition violation!\nRangeHistogramBase::setMinMax(...): setBinCount(...) has not been called.");
            std::string message(c.what());
            shouldEqual(expected, message.substr(0,expected.size()));
        }

        try 
        {
            A b;
            getAccumulator<UserRangeHistogram<0> >(b).setBinCount(HSIZE+2);
            getAccumulator<UserRangeHistogram<0> >(b).setMinMax(-2.5, 12.5);
            extractFeatures(data, data+SIZE, b);
            failTest("extractFeatures() failed to throw exception");
        }
        catch(ContractViolation & c) 
        {
            std::string expected("\nPrecondition violation!\nRangeHistogramBase::setMinMax(...): setBinCount(...) has not been called.");
            std::string message(c.what());
            shouldEqual(expected, message.substr(0,expected.size()));
        }

        try 
        {
            A b;
            b.setHistogramOptions(HistogramOptions().setBinCount(HSIZE));
            getAccumulator<UserRangeHistogram<0> >(b).setMinMax(-2.5, 12.5);

            extractFeatures(data, data+SIZE, b);
            a.merge(b);

            failTest("extractFeatures() failed to throw exception");
        }
        catch(ContractViolation & c) 
        {
            std::string expected("\nPrecondition violation!\nRangeHistogramBase::operator+=(): cannot merge histograms with different data mapping.");
            std::string message(c.what());
            shouldEqual(expected, message.substr(0,expected.size()));
        }

        A b;
        b.setHistogramOptions(HistogramOptions().setBinCount(HSIZE).setMinMax(-0.5, 9.5));

        extractFeatures(data, data+SIZE, b);
        a.merge(b);

        TinyVector<double, HSIZE> h2 = TinyVector<double, HSIZE>(h)*2.0;
        shouldEqualSequence(h2.begin(), h2.end(), get<UserRangeHistogram<0> >(a).begin());
        shouldEqualSequence(h2.begin(), h2.end(), get<AutoRangeHistogram<0> >(a).begin());
        shouldEqualSequence(h2.begin(), h2.end(), get<IntegerHistogram<0> >(a).begin());
    }
}


template <class Accumulator>
typename Accumulator::PythonBase *
myPythonRegionInspect(NumpyArray<2, Singleband<npy_float32> > in, 
                      NumpyArray<2, Singleband<npy_uint32> > labels)
{
    typedef typename CoupledIteratorType<2, npy_float32, npy_uint32>::type Iterator;
    
    TinyVector<npy_intp, 2> permutation = in.template permuteLikewise<2>();
    
    VIGRA_UNIQUE_PTR<Accumulator> res(new Accumulator(permutation));
            
    PyAllowThreads _pythread;
    
    Iterator i     = createCoupledIterator(in, labels),
                end   = i.getEndIterator();
    extractFeatures(i, end, *res);
    
    return res.release();
}

void testGlue()
{
    NumpyArray<2, Singleband<npy_float32> > vol;
    NumpyArray<2, Singleband<npy_uint32> > labels;
    
    typedef typename CoupledIteratorType<2, npy_float32, npy_uint32>::type Iterator;
    typedef typename Iterator::value_type Handle;
    
    using namespace vigra::acc;

    typedef Select<Count, Mean, Variance, Skewness, Kurtosis, 
                   Minimum, Maximum, StandardQuantiles<GlobalRangeHistogram<0> >,
                   RegionCenter, RegionRadii, RegionAxes,
                   Weighted<RegionCenter>, Weighted<RegionRadii>, Weighted<RegionAxes>,
                   Select<Coord<Minimum>, Coord<Maximum>, Coord<ArgMinWeight>, Coord<ArgMaxWeight>, 
                          Principal<Coord<Skewness> >, Principal<Coord<Kurtosis> >, 
                          Principal<Weighted<Coord<Skewness> > >, Principal<Weighted<Coord<Kurtosis> > > >,
                   DataArg<1>, WeightArg<1>, LabelArg<2>
                   > ScalarRegionAccumulators;
    
    typedef PythonAccumulator<DynamicAccumulatorChainArray<Handle, ScalarRegionAccumulators>, 
                                    PythonRegionFeatureAccumulator, GetArrayTag_Visitor> Accu;
    
    myPythonRegionInspect<Accu>(vol, labels);
}


int main(int c, char** v) 
{
    struct rusage ru;
    for (unsigned long long int i=0; 1; i++) {
        if (i%1000) {
            getrusage(RUSAGE_SELF, &ru);
            std::cerr << ru.ru_maxrss << std::endl;
        }
        testRegionAccumulators();
        testHistogram();
        testGlue();
    }
    return 0;
}