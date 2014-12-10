#! /usr/bin/env python
# -*- coding: utf8 -*-

"""
This script adds a license file to a DMG. Requires Xcode and a plain ascii text
license file.
Obviously only runs on a Mac.

Copyright (C) 2011 Jared Hobbs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import os
import sys
import tempfile
import optparse


class Path(str):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # comment below out to see the temp file
        os.unlink(self)
        # print 'no delete'


def mktemp(dir=None, suffix=''):
    (fd, filename) = tempfile.mkstemp(dir=dir, suffix=suffix)
    os.close(fd)
    return Path(filename)


# @see http://www.owsiak.org/?p=700
# but relace """data 'LPic' (5000) ... """ part with the full code
# @see https://github.com/andreyvit/yoursway-create-dmg

def main(options, args):
    dmgFile, license = args
    with mktemp('.') as tmpFile:
        print 'tmpFile: '
        print tmpFile
        with open(tmpFile, 'w') as f:
            # all languages added
            f.write("""data 'LPic' (5000) {
    $"0002 0011 0003 0001 0000 0000 0002 0000"
    $"0008 0003 0000 0001 0004 0000 0004 0005"
    $"0000 000E 0006 0001 0005 0007 0000 0007"
    $"0008 0000 0047 0009 0000 0034 000A 0001"
    $"0035 000B 0001 0020 000C 0000 0011 000D"
    $"0000 005B 0004 0000 0033 000F 0001 000C"
    $"0010 0000 000B 000E 0000"
};\n\n""")
            with open(license, 'r') as l:
                f.write('data \'TEXT\' (5010, "Simplified Chinese") {\n')
                for line in l:
                    if len(line) < 1000:
                        f.write('    "' + line.strip().replace('"', '\\"').decode("utf8").encode("gbk") + '\\n"\n')
                    else:
                        for liner in line.split('.'):
                            f.write('    "' +
                                    liner.strip().replace('"', '\\"').decode("utf8").encode("gbk") + '. \\n"\n')
                f.write('};\n\n')

            f.write("""data 'STR#' (5010, "Simplified Chinese") {
    $"0006 1253 696D 706C 6966 6965 6420 4368"            /* ...Simplified Ch */
    $"696E 6573 6504 CDAC D2E2 06B2 BBCD ACD2"            /* inese.Õ¨“‚.≤ªÕ¨“ */
    $"E204 B4F2 D3A1 06B4 E6B4 A2A1 AD54 C8E7"            /* ‚.¥Ú”°.¥Ê¥¢°≠T»Á */
    $"B9FB C4FA CDAC D2E2 B1BE D0ED BFC9 D0AD"            /* π˚ƒ˙Õ¨“‚±æ–Ìø…–≠ */
    $"D2E9 B5C4 CCF5 BFEE A3AC C7EB B0B4 A1B0"            /* “ÈµƒÃıøÓ£¨«Î∞¥°∞ */
    $"CDAC D2E2 A1B1 C0B4 B0B2 D7B0 B4CB C8ED"            /* Õ¨“‚°±¿¥∞≤◊∞¥À»Ì */
    $"BCFE A1A3 C8E7 B9FB C4FA B2BB CDAC D2E2"            /* º˛°£»Áπ˚ƒ˙≤ªÕ¨“‚ */
    $"A3AC C7EB B0B4 A1B0 B2BB CDAC D2E2 A1B1"            /* £¨«Î∞¥°∞≤ªÕ¨“‚°± */
    $"A1A3"   
};\n\n""")
        os.system('/usr/bin/hdiutil unflatten -quiet "%s"' % dmgFile)
        os.system('%s "%s/"*.r %s -a -o "%s"' %
                  (options.rez, options.flat_carbon, tmpFile, dmgFile))

        os.system('/usr/bin/hdiutil flatten -quiet "%s"' % dmgFile)
        if options.compression is not None:
            os.system('cp %s %s.temp.dmg' % (dmgFile, dmgFile))
            os.remove(dmgFile)
            if options.compression == "bz2":
                os.system('hdiutil convert %s.temp.dmg -format UDBZ -o %s' %
                          (dmgFile, dmgFile))
            elif options.compression == "gz":
                os.system('hdiutil convert %s.temp.dmg -format ' % dmgFile +
                          'UDZO -imagekey zlib-devel=9 -o %s' % dmgFile)
            os.remove('%s.temp.dmg' % dmgFile)
    print "Successfully added license to '%s'" % dmgFile

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.set_usage("""%prog <dmgFile> <licenseFile> [OPTIONS]
  This program adds a software license agreement to a DMG file.
  It requires Xcode and a plain ascii text <licenseFile>.

  See --help for more details.""")
    parser.add_option(
        '--rez',
        '-r',
        action='store',
        default='/Applications/Xcode.app/Contents/Developer/Tools/Rez',
        help='The path to the Rez tool. Defaults to %default'
    )
    parser.add_option(
        '--flat-carbon',
        '-f',
        action='store',
        default='/Applications/Xcode.app/Contents/Developer/Platforms'
                '/MacOSX.platform/Developer/SDKs/MacOSX10.7.sdk'
                '/Developer/Headers/FlatCarbon',
        help='The path to the FlatCarbon headers. Defaults to %default'
    )
    parser.add_option(
        '--compression',
        '-c',
        action='store',
        choices=['bz2', 'gz'],
        default=None,
        help='Optionally compress dmg using specified compression type. '
             'Choices are bz2 and gz.'
    )
    options, args = parser.parse_args()
    cond = len(args) != 2 or not os.path.exists(options.rez) \
        or not os.path.exists(options.flat_carbon)
    if cond:
        parser.print_usage()
        sys.exit(1)
    main(options, args)
