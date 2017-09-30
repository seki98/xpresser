#
# Copyright (c) 2010 Canonical
#
# Written by Gustavo Niemeyer <gustavo@niemeyer.net>
#
# This file is part of the Xpresser GUI automation library.
#
# Xpresser is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3,
# as published by the Free Software Foundation.
#
# Xpresser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from xpresser.imagematch import ImageMatch
import cv2
import numpy
from matplotlib import pyplot as plt

FILTER_MARGIN = 25 # %


class OpenCVFinder(object):

    def find(self, screen_image, area_image):
        matches = self._find(screen_image, area_image, best_match=True)
        if matches:
            return matches[0]
        return None

    def find_all(self, screen_image, area_image):
        return self._find(screen_image, area_image)

    def _load_image(self, image):
        if "opencv_image" not in image.cache:
            if image.filename is not None:
                opencv_image = cv2.imread(image.filename)
            elif image.array is not None:
                opencv_image = image.array
            else:
                raise RuntimeError("Oops. Can't load image.")
            image.cache["opencv_image"] = opencv_image
            image.width = image.width
            image.height = image.height
        return image.cache["opencv_image"]

    def _find(self, screen_image, area_image, best_match=False):
        source = self._load_image(screen_image)
        template = self._load_image(area_image)
        results = []
        cv2.waitKey(1000)
        matches = cv2.matchTemplate(source, template, 5)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matches)

        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        top_left = max_loc
        w, h = 800,640
        bottom_right = (top_left[0] + w, top_left[1] + h)

        #cv2.rectangle(source, top_left, bottom_right, 255, 2)

        #plt.subplot(121), plt.imshow(template, cmap='gray')
        #plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        #plt.subplot(122), plt.imshow(source, cmap='gray')
        #plt.title('Detected Point'), plt.xticks([]), plt.yticks([])

        #plt.show()


        res = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = numpy.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(source, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        print(loc)
        cv2.imwrite('res.png', source)


        #if matches is not None:
        #    for m in [m for m in matches if 0.99 >= area_image.similarity]:
        #        results.append(
        #            ImageMatch(area_image, m.x, m.y, m.quality))
        #        if best_match and m.quality == 1.0:
        #            return [results[-1]]
        #x_margin = int(FILTER_MARGIN/100.0 * 860)
        #y_margin = int(FILTER_MARGIN/100.0 * 600)

        #results = self._filter_nearby_positions(results, x_margin, y_margin)
        #if results:
        #    results.sort(key=lambda match: -match.similarity)

        return loc

    def _filter_nearby_positions(self, matches, x_margin, y_margin):
        """Remove nearby positions by taking the best one.

        Doing this is necessary because around a good match there will
        likely be other worse matches.
        """

        # We have to build a kill list rather than removing on the fly
        # so that neighbors of neighbors get correctly processed.
        kill = set()
        for match1 in matches:
            if match1 in kill:
                # Another match has already figured that this one isn't good.
                continue
            for match2 in matches:
                if match2 is match1:
                    continue
                # Even if match2 is in the kill list, we have to process it
                # because it may have a better rating than this one still, and
                # this would mean someone around is even better than match2,
                # and thus both match2 *and* match1 should be killed.
                #distance = math.hypot(match2.x-match1.x, match2.y-match1.y)
                #if distance <= filter_distance:
                if (abs(match2.x-match1.x) < x_margin or
                    abs(match2.y-match1.y) < y_margin):
                    comparison = cmp(match1.similarity, match2.similarity)
                    if comparison > 0:
                        # match2 is worse, so ensure it's in the kill list
                        # and maybe save time later on (if indeed it wasn't yet).
                        kill.add(match2)
                    elif (comparison < 0
                        or (comparison == 0 and match2 not in kill)):
                        # If match2 matches better than match1, or they're
                        # equivalent and match2 is not in the kill list yet,
                        # so kill match1 and move on to a different match1.
                        kill.add(match1)
                        break

        return list(set(matches) - kill)
