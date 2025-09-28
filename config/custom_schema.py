"""
Custom OpenAPI schema generator for filtering by tags
"""

from django.urls import URLPattern, URLResolver

from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.openapi import AutoSchema


class TagFilteredSchemaGenerator(SchemaGenerator):
    """Custom schema generator that filters endpoints by tags"""

    def __init__(self, *args, **kwargs):
        self.target_tags = kwargs.pop("target_tags", [])
        super().__init__(*args, **kwargs)

    def get_paths(self, request=None):
        """Override to filter paths by tags before processing"""
        paths = super().get_paths(request)

        if not self.target_tags:
            return paths

        filtered_paths = {}

        for path, path_item in paths.items():
            should_include = False
            filtered_methods = {}

            for method, operation in path_item.items():
                if method.startswith("_"):  # Skip internal attributes
                    continue

                operation_tags = operation.get("tags", [])
                print(f"Path: {path}, Method: {method.upper()}, Tags: {operation_tags}")

                if operation_tags and any(tag in self.target_tags for tag in operation_tags):
                    should_include = True
                    filtered_methods[method] = operation
                    print(f"✓ Including {method.upper()} {path}")

            if should_include:
                filtered_paths[path] = filtered_methods

        print(f"Filtered {len(filtered_paths)} paths from {len(paths)} total paths")
        return filtered_paths


class CategoryAutoSchema(AutoSchema):
    """Custom AutoSchema for individual endpoints"""

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        return operation
