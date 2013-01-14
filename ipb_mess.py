from collections import OrderedDict
import re


def _make_str_replacer(pattern, replace):
    def replacer(value):
        return value.replace(pattern, replace)
    return replacer

def _make_regex_replacer(pattern, replace):
    regex_pattern = re.compile(pattern)
    def replacer(value):
        return regex_pattern.sub(replace, value)
    return replacer

_simple_value_replaces = [
    _make_str_replacer("&#032;", " "),
    _make_str_replacer("&"            , "&amp;"),
    _make_str_replacer("<!--"         , "&#60;&#33;--"),
    _make_str_replacer("-->"          , "--&#62;"),
    _make_regex_replacer("(?i)<script", "&#60;script"),
    _make_str_replacer(">"            , "&gt;"),
    _make_str_replacer("<"            , "&lt;"),
    _make_str_replacer("\""           , "&quot;"),
    #_make_regex_replacer("/\n/"        , "<br />"),
    #_make_regex_replacer("/\\\$/"      , "&#036;" ),
    #_make_regex_replacer("/\r/"        , ""),
    _make_str_replacer("!"            , "&#33;"),
    _make_str_replacer("'"            , "&#39;"),]


#    function clean_value($val)
#    {
#                global $ibforums;
#
#        if ($val == "")
#        {
#                return "";
#        }
#
#        $val = str_replace( "&#032;", " ", $val );
#
#        if ( $ibforums->vars['strip_space_chr'] )
#        {
#                $val = str_replace( chr(0xCA), "", $val );  //Remove sneaky spaces
#        }
#
#        $val = str_replace( "&"            , "&amp;"         , $val );
#        $val = str_replace( "<!--"         , "&#60;&#33;--"  , $val );
#        $val = str_replace( "-->"          , "--&#62;"       , $val );
#        $val = preg_replace( "/<script/i"  , "&#60;script"   , $val );
#        $val = str_replace( ">"            , "&gt;"          , $val );
#        $val = str_replace( "<"            , "&lt;"          , $val );
#        $val = str_replace( "\""           , "&quot;"        , $val );
#        $val = preg_replace( "/\n/"        , "<br />"        , $val ); // Convert literal newlines
#        $val = preg_replace( "/\\\$/"      , "&#036;"        , $val );
#        $val = preg_replace( "/\r/"        , ""              , $val ); // Remove literal carriage returns
#        $val = str_replace( "!"            , "&#33;"         , $val );
#        $val = str_replace( "'"            , "&#39;"         , $val ); // IMPORTANT: It helps to increase sql query safety.
#
#        // Ensure unicode chars are OK
#
#        if ( $this->allow_unicode )
#                {
#                        $val = preg_replace("/&amp;#([0-9]+);/s", "&#\\1;", $val );
#                }
#
#                // Strip slashes if not already done so.
#
#        if ( $this->get_magic_quotes )
#        {
#                $val = stripslashes($val);
#        }
#
#        // Swop user inputted backslashes
#
#        $val = preg_replace( "/\\\(?!&amp;#|\?#)/", "&#092;", $val );
#
#        return $val;
#    }



def ipb_clean_value(value):
    for replacer in _simple_value_replaces:
        value = replacer(value)
    return value