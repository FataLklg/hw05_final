from django.core.paginator import Paginator

COUNT_PAGES: int = 10  # Константа выборки постов для вывода на страницу


def paginator(request, post_list):
    paginator = Paginator(post_list, COUNT_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
