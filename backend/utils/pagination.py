from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class SmartPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that preserves pagination state on delete operations.
    When an item is deleted, it returns the same page if possible, or the last page if the current page becomes empty.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'page_size': self.get_page_size(self.request),
            'results': data,
        })
    
    def get_paginated_response_for_delete(self, data, deleted_count=1):
        """
        Special response for delete operations that preserves pagination state.
        """
        paginator = self.page.paginator
        current_page = self.page.number
        total_count = paginator.count
        page_size = self.get_page_size(self.request)
        
        # Calculate the new total pages after deletion
        new_total_count = total_count - deleted_count
        new_total_pages = (new_total_count + page_size - 1) // page_size if new_total_count > 0 else 1
        
        # Determine the page to return after deletion
        if new_total_count == 0:
            # No items left, return page 1
            target_page = 1
        elif current_page > new_total_pages:
            # Current page no longer exists, return the last page
            target_page = new_total_pages
        else:
            # Current page still exists, stay on it
            target_page = current_page
        
        # Build the next/previous links for the target page
        next_link = None
        previous_link = None
        
        if target_page < new_total_pages:
            next_link = self.build_absolute_uri(self.request.build_absolute_uri().split('?')[0], {
                self.page_query_param: target_page + 1,
                self.page_size_query_param: page_size
            })
        
        if target_page > 1:
            previous_link = self.build_absolute_uri(self.request.build_absolute_uri().split('?')[0], {
                self.page_query_param: target_page - 1,
                self.page_size_query_param: page_size
            })
        
        return Response({
            'count': new_total_count,
            'next': next_link,
            'previous': previous_link,
            'current_page': target_page,
            'total_pages': new_total_pages,
            'page_size': page_size,
            'results': data,
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} item(s)',
        })
    
    def build_absolute_uri(self, base_url, params):
        """
        Build absolute URI with query parameters.
        """
        from urllib.parse import urlencode
        query_string = urlencode(params)
        return f"{base_url}?{query_string}" if query_string else base_url


class PreserveStatePagination(SmartPageNumberPagination):
    """
    Pagination class that automatically handles pagination state preservation.
    Use this in viewsets that need to maintain pagination state on delete operations.
    """
    
    def get_paginated_response(self, data, deleted_count=None):
        """
        Override to handle both normal responses and delete responses.
        """
        if deleted_count is not None:
            return self.get_paginated_response_for_delete(data, deleted_count)
        return super().get_paginated_response(data) 