(define
    (domain garden)
    (:requirements :strips :typing)
    (:types
        state - object
        world - object
    )

    (:predicates
        (dummy1 ?s - state)
        
        (raining ?w - world)

        (tank-full ?s - state)
        (refill-indicator-light-on ?s - state)
        (low-soil-hum ?s - state)

        (too-bright ?s - state)
        (too-dark ?s - state)
        (lamp-on ?s - state)

        (too-warm ?s - state)
        (too-cold ?s - state)
        (fan-on ?s - state)

        (lid-open ?s - state)
    )

   (:action TURN_ON_LIGHT
        :parameters (?s - state)
        :precondition (and
            (too-dark ?s)
            (not (lamp-on ?s))
        )
        :effect (and
            (not (too-dark ?s))
            (lamp-on ?s)
        )
    )

    (:action TURN_OFF_LIGHT
        :parameters (?s - state)
        :precondition (and
            (too-bright ?s)
            (lamp-on ?s)
        )
        :effect (and
            (not (too-bright ?s))
            (not (lamp-on ?s))
        )
    )

    (:action TURN_ON_FAN
        :parameters (?s - state ?w - world)
        :precondition (and
            (too-warm ?s)
            (raining ?w)
            (not (fan-on ?s))
        )
        :effect (and
            (not (too-warm ?s))
            (fan-on ?s)
        )
    )

    (:action TURN_OFF_FAN
        :parameters (?s - state)
        :precondition (and
            (too-cold ?s)
            (fan-on ?s)
        )
        :effect (and
            (not (too-cold ?s))
            (not (fan-on ?s))
        )
    )

    (:action OPEN_LID
        :parameters (?s - state ?w - world)
        :precondition (and
            (too-warm ?s)
            (not(raining ?w))
            (not (lid-open ?s))
        )
        :effect (and
            (not (too-warm ?s))
            (lid-open ?s)
        )
    )

    (:action CLOSE_LID
        :parameters (?s - state ?w - world)
        :precondition (and
            (or(too-cold ?s)(raining ?w))
            (lid-open ?s)
        )
        :effect (and
            (not (too-cold ?s))
            (not (lid-open ?s))
        )
    )

    (:action WATER_PLANT
        :parameters (?s - state)
        :precondition (and
            (tank-full ?s)
            (low-soil-hum ?s)
        )
        :effect (and
            (not (low-soil-hum ?s))
        )
    )

    (:action REFILL_TANK_LIGHT_ON
        :parameters (?s - state)
        :precondition (and
            (not(tank-full ?s))
            (not(refill-indicator-light-on ?s))
        )
        :effect (and
            (refill-indicator-light-on ?s)
        )
    )

    (:action REFILL_TANK_LIGHT_OFF
        :parameters (?s - state)
        :precondition (and
            (tank-full ?s)
            (refill-indicator-light-on ?s)
        )
        :effect (and
            (not(refill-indicator-light-on ?s))
        )
    )
)
