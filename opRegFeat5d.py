# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 18:43:20 2015

@author: burger
"""

import numpy as np
import vigra

from lazyflow.operator import Operator, InputSlot, OutputSlot
from lazyflow.rtype import List
from lazyflow.stype import Opaque


class OpRegionFeatures5d(Operator):
    """Produces region features for a 3d image.

    The image's axes are extended to the full txyzc shape.

    Inputs:

    * RawVolume : the raw data on which to compute features

    * LabelVolume : a volume of connected components for each object
      in the raw data.

    * Features : a nested dictionary of features to compute.
      Features[plugin name][feature name][parameter name] = parameter value

    Outputs:

    * Output : a nested dictionary of features.
      Output[plugin name][feature name] = numpy.ndarray

    """
    RawVolume = InputSlot()
    LabelVolume = InputSlot()
    Features = InputSlot(rtype=List, stype=Opaque)

    Output = OutputSlot()

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)

        self.

    def setupOutputs(self):
        if self.LabelVolume.meta.axistags != self.RawVolume.meta.axistags:
            raise Exception('raw and label axis tags do not match')

        taggedOutputShape = self.LabelVolume.meta.getTaggedShape()
        taggedRawShape = self.RawVolume.meta.getTaggedShape()

        if not np.all(list(taggedOutputShape.get(k, 0) == taggedRawShape.get(k, 0)
                           for k in "txyz")):
            raise Exception("shapes do not match. label volume shape: {}."
                            " raw data shape: {}".format(
                                self.LabelVolume.meta.shape,
                                self.RawVolume.meta.shape))

        self.Output.meta.shape = (taggedOutputShape['t'],)
        self.Output.meta.axistags = vigra.defaultAxistags('t')
        # The features for the entire block (in xyz) are provided for the requested tc coordinates.
        self.Output.meta.dtype = object

    def execute(self, slot, subindex, roi, result):
        assert len(roi.start) == len(roi.stop) == len(self.Output.meta.shape)
        assert slot == self.Output

        t_ind = self.RawVolume.axistags.index('t')
        assert t_ind < len(self.RawVolume.meta.shape)

        # loop over requested time slices
        for res_t_ind, t in enumerate(xrange(roi.start[t_ind],
                                             roi.stop[t_ind])):
            
            # Process entire spatial volume
            s = [slice(None) for i in range(len(self.RawVolume.meta.shape))]
            s[t_ind] = slice(t, t+1)
            s = tuple(s)
            rawVolume = self.RawVolume[s].wait()
            rawVolume = vigra.taggedView(
                rawVolume, axistags=self.RawVolume.meta.axistags)
            labelVolume = self.LabelVolume[s].wait()
            labelVolume = vigra.taggedView(
                labelVolume, axistags=self.LabelVolume.meta.axistags)
    
            # Convert to 4D (preserve axis order)
            axes4d = self.RawVolume.meta.getTaggedShape().keys()
            axes4d = filter(lambda k: k in 'xyzc', axes4d)
            rawVolume = rawVolume.withAxes(*axes4d)
            labelVolume = labelVolume.withAxes(*axes4d)
            acc = self._extract(rawVolume4d, labelVolume4d)
            result[res_t_ind] = acc
        
        return result

    def compute_extent(self, i, image, mincoords, maxcoords, axes, margin):
        """Make a slicing to extract object i from the image."""
        #find the bounding box (margin is always 'xyz' order)
        result = [None] * 3
        minx = max(mincoords[i][axes.x] - margin[axes.x], 0)
        miny = max(mincoords[i][axes.y] - margin[axes.y], 0)

        # Coord<Minimum> and Coord<Maximum> give us the [min,max]
        # coords of the object, but we want the bounding box: [min,max), so add 1
        maxx = min(maxcoords[i][axes.x] + 1 + margin[axes.x], image.shape[axes.x])
        maxy = min(maxcoords[i][axes.y] + 1 + margin[axes.y], image.shape[axes.y])

        result[axes.x] = slice(minx, maxx)
        result[axes.y] = slice(miny, maxy)

        try:
            minz = max(mincoords[i][axes.z] - margin[axes.z], 0)
            maxz = min(maxcoords[i][axes.z] + 1 + margin[axes.z], image.shape[axes.z])
        except:
            minz = 0
            maxz = 1

        result[axes.z] = slice(minz, maxz)

        return result

    def compute_rawbbox(self, image, extent, axes):
        """essentially returns image[extent], preserving all channels."""
        key = copy(extent)
        key.insert(axes.c, slice(None))
        return image[tuple(key)]

    def _extract(self, image, labels):
        if not (image.ndim == labels.ndim == 4):
            raise Exception("both images must be 4D. raw image shape: {}"
                            " label image shape: {}".format(image.shape, labels.shape))

        # FIXME: maybe simplify? taggedShape should be easier here
        class Axes(object):
            x = image.axistags.index('x')
            y = image.axistags.index('y')
            z = image.axistags.index('z')
            c = image.axistags.index('c')
        axes = Axes()

        slc3d = [slice(None)] * 4 # FIXME: do not hardcode
        slc3d[axes.c] = 0

        labels = labels[slc3d]
        
        logger.debug("Computing default features")

        feature_names = deepcopy(self.Features([]).wait())

        # do global features
        logger.debug("computing global features")
        extra_features_computed = False
        global_features = {}
        selected_vigra_features = []
        for plugin_name, feature_dict in feature_names.iteritems():
            plugin = pluginManager.getPluginByName(plugin_name, "ObjectFeatures")
            if plugin_name == "Standard Object Features":
                #expand the feature list by our default features
                logger.debug("attaching default features {} to vigra features {}".format(default_features, feature_dict))
                selected_vigra_features = feature_dict.keys()
                feature_dict.update(default_features)
                extra_features_computed = True
            global_features[plugin_name] = plugin.plugin_object.compute_global(image, labels, feature_dict, axes)
        
        extrafeats = {}
        if extra_features_computed:
            for feat_key in default_features:
                feature = None
                if feat_key in selected_vigra_features:
                    #we wanted that feature independently
                    feature = global_features["Standard Object Features"][feat_key]
                else:
                    feature = global_features["Standard Object Features"].pop(feat_key)
                    feature_names["Standard Object Features"].pop(feat_key)
                extrafeats[feat_key] = feature
        else:
            logger.debug("default features not computed, computing separately")
            extrafeats_acc = vigra.analysis.extractRegionFeatures(image[slc3d].squeeze().astype(np.float32), labels.squeeze(),
                                                        default_features.keys(),
                                                        ignoreLabel=0)
            #remove the 0th object, we'll add it again later
            for k, v in extrafeats_acc.iteritems():
                extrafeats[k]=v[1:]
                if len(v.shape)==1:
                    extrafeats[k]=extrafeats[k].reshape(extrafeats[k].shape+(1,))
        
        extrafeats = dict((k.replace(' ', ''), v)
                          for k, v in extrafeats.iteritems())
        
        mincoords = extrafeats["Coord<Minimum>"]
        maxcoords = extrafeats["Coord<Maximum>"]
        nobj = mincoords.shape[0]
        
        # local features: loop over all objects
        def dictextend(a, b):
            for key in b:
                a[key].append(b[key])
            return a
        

        local_features = defaultdict(lambda: defaultdict(list))
        margin = max_margin(feature_names)
        has_local_features = {}
        for plugin_name, feature_dict in feature_names.iteritems():
            has_local_features[plugin_name] = False
            for features in feature_dict.itervalues():
                if 'margin' in features:
                    has_local_features[plugin_name] = True
                    break
            
                            
        if np.any(margin) > 0:
            #starting from 0, we stripped 0th background object in global computation
            for i in range(0, nobj):
                logger.debug("processing object {}".format(i))
                extent = self.compute_extent(i, image, mincoords, maxcoords, axes, margin)
                rawbbox = self.compute_rawbbox(image, extent, axes)
                #it's i+1 here, because the background has label 0
                binary_bbox = np.where(labels[tuple(extent)] == i+1, 1, 0).astype(np.bool)
                for plugin_name, feature_dict in feature_names.iteritems():
                    if not has_local_features[plugin_name]:
                        continue
                    plugin = pluginManager.getPluginByName(plugin_name, "ObjectFeatures")
                    feats = plugin.plugin_object.compute_local(rawbbox, binary_bbox, feature_dict, axes)
                    local_features[plugin_name] = dictextend(local_features[plugin_name], feats)

        logger.debug("computing done, removing failures")
        # remove local features that failed
        for pname, pfeats in local_features.iteritems():
            for key in pfeats.keys():
                value = pfeats[key]
                try:
                    pfeats[key] = np.vstack(list(v.reshape(1, -1) for v in value))
                except:
                    logger.warn('feature {} failed'.format(key))
                    del pfeats[key]

        # merge the global and local features
        logger.debug("removed failed, merging")
        all_features = {}
        plugin_names = set(global_features.keys()) | set(local_features.keys())
        for name in plugin_names:
            d1 = global_features.get(name, {})
            d2 = local_features.get(name, {})
            all_features[name] = dict(d1.items() + d2.items())
        all_features[default_features_key]=extrafeats

        # reshape all features
        for pfeats in all_features.itervalues():
            for key, value in pfeats.iteritems():
                if value.shape[0] != nobj:
                    raise Exception('feature {} does not have enough rows, {} instead of {}'.format(key, value.shape[0], nobj))

                # because object classification operator expects nobj to
                # include background. FIXME: we should change that assumption.
                value = np.vstack((np.zeros(value.shape[1]),
                                   value))
                value = value.astype(np.float32) #turn Nones into numpy.NaNs

                assert value.dtype == np.float32
                assert value.shape[0] == nobj+1
                assert value.ndim == 2

                pfeats[key] = value
        logger.debug("merged, returning")
        return all_features

    def propagateDirty(self, slot, subindex, roi):
        if slot is self.Features:
            self.Output.setDirty(slice(None))
        else:
            axes = self.RawVolume.meta.getTaggedShape().keys()
            dirtyStart = collections.OrderedDict(zip(axes, roi.start))
            dirtyStop = collections.OrderedDict(zip(axes, roi.stop))

            # Remove the spatial and channel dims (keep t, if present)
            del dirtyStart['x']
            del dirtyStart['y']
            del dirtyStart['z']
            del dirtyStart['c']

            del dirtyStop['x']
            del dirtyStop['y']
            del dirtyStop['z']
            del dirtyStop['c']

            self.Output.setDirty(dirtyStart.values(), dirtyStop.values())