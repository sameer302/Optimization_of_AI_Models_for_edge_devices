### File naming convention:-
word -> number of cores
number -> core number

first_part -> threads related to code
second_part -> threads related to isolation
third_part -> threads related to affinity

### Observations:- 
1) Number of threads the inference breaks into and running threads (average and approximate):
    1) all_zero_all --> 20  2
    2) three_zero_all --> 18
    3) four_zero_all --> 22/21
    4) five_zero_all --> 

2) Average FPS and Latency:
    1) all_zero_all --> 2.624   388.045