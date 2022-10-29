"""
반복 가능한 객체를 다루는 모듈

유용한 제너레이터
"""
from .custom_itertools import (
    common_starts,
    dowhile,
    every_nth,
    get_duplicate_items,
    get_sorted_order,
    group_by_interval,
    index_pred,
    iterable_with_callback,
    iterate,
    multi_sorted,
    pairs,
    skipper,
    slice_items,
    sort_by_specific_order,
)
from .itertools_recipe import (
    all_equal,
    consume,
    dotproduct,
    first_true,
    flatten,
    grouper,
    iter_except,
    ncycles,
    nth,
    padnone,
    pairwise,
    partition,
    powerset,
    quantify,
    random_combination,
    random_combination_with_replacement,
    random_permutation,
    random_product,
    repeatfunc,
    roundrobin,
    tabulate,
    tail,
    take,
    unique_everseen,
    unique_justseen,
)
