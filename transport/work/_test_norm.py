# -*- coding: utf-8 -*-
import _clean_all_noise as cn
s = '<table>\n  <tbody>\n    <!-- 左侧 1~50，右侧 51~100 逐行对应 -->\n    <tr><td>x</td></tr>\n  </tbody>\n</table>'
print("原始:", repr(s))
print("清理:", repr(cn.normalize(s)))
print("含注释?", "<!--" in cn.normalize(s))
