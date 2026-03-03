def build_menu_tree(menus, parent=None):
    """
    Recursive function to build a hierarchical menu tree.
    Can receive a queryset or a list of Menu instances.
    """
    tree = []
    level_menus = [m for m in menus if m.parent == parent]
    level_menus.sort(key=lambda x: x.ordering)

    for menu in level_menus:
        node = {
            "id": str(menu.id),
            "subject": menu.subject,
            "description": menu.description,
            "title": menu.title,
            "icon": menu.icon,
            "ordering": menu.ordering,
            "to": menu.to or "root",
            "children": build_menu_tree(menus, parent=menu),
        }
        tree.append(node)

    return tree
