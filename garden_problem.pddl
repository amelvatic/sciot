(define
    (problem gardenproblem)
    (:domain garden)
    (:objects 
        s - state
        w -world
    )
    (:init 
        (dummy1 s)
        
   )
     (:goal (and
            (and(or (tank-full s) (refill-indicator-light-on s))(not(and(refill-indicator-light-on s)(tank-full s))))
            (not(too-bright s))
            (not(too-dark s))
            (not(too-cold s))
            (not(too-warm s))
            (not (low-soil-hum s))
        )
     )
     )
