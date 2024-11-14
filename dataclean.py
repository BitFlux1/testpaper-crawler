import re
import urllib.parse
from bs4 import BeautifulSoup


def html_to_latex(element):
    """递归转换HTML子元素为LaTeX格式"""
    if isinstance(element, str):
        return element

    latex = ""
    for child in element.children:
        if child.name == "sup":
            latex += "^{" + html_to_latex(child) + "}"
        elif child.name == "sub":
            latex += "_{" + html_to_latex(child) + "}"
        elif child.name == "img" and not child.has_attr("data-latex"):
            latex += str(child)
        else:
            latex += html_to_latex(child)

    return latex


def clean_html(html_content, keep_newlines=True, keep_images=True):
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 删除所有<style>标签及其内容
    for style in soup.find_all('style'):
        style.decompose()

    # 处理具有data-latex属性的元素
    for latex_element in soup.find_all(attrs={"data-latex": True}):
        latex_code = latex_element['data-latex']
        decoded_latex = urllib.parse.unquote(latex_code)
        latex_element.replace_with(decoded_latex)

    # 转换sup和sub标签为LaTeX格式
    for sup in soup.find_all('sup'):
        latex_sup = "^{" + sup.text + "}"
        sup.replace_with(latex_sup)

    for sub in soup.find_all('sub'):
        latex_sub = "_{" + sub.text + "}"
        sub.replace_with(latex_sub)

    # 根据keep_images参数控制是否保留<img>标签
    text_with_images = ""
    for element in soup.descendants:
        if element.name == "img" and not element.has_attr("data-latex"):
            if keep_images:
                text_with_images += str(element)
        elif isinstance(element, str):
            if keep_newlines:
                text_with_images += element
            else:
                text_with_images += element.replace("\n", "")
        else:
            text_with_images += html_to_latex(element)

    if keep_newlines:
        # 用正则表达式恢复\n
        text_with_images = re.sub(r"(?<!>)\s*(?=<)", "\n", text_with_images)

    return text_with_images



