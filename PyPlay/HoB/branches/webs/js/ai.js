define( function() {
    function WorldState( properties ) {
        if( properties ) this.apply( properties );
    }
    WorldState.prototype.basic_keys = [
        "RCSFuel", "weaponCool", "targetDestroyed", "aligned" ];

    WorldState.prototype.build = function( parent, target, weapon ) {
        this.RCSFuel = true;
        this.weaponCool = true;
        this.targetDestroyed = false;

        this.parent = parent;
        this.target = target;
        this.targetDir = target.body.position.vsub( parent.body.position );
        this.targetDir.normalize();

        this.aligned = parent.body.vectorToWorldFrame(
            new CANNON.Vec3( 0, 0, -1 ) ).dot( this.targetDir ) > 0.9;
    }

    WorldState.prototype.distance = function( other ) {
        result = 0;
        for( key of this.basic_keys  )
            if( this[key] !== undefined && other[key] !== undefined &&
                this[key] != other[key] )
                result += 2;
        return result;
    }

    WorldState.prototype.fulfills = function( properties ) {
        for( key of this.basic_keys ) 
            if( properties[key] !== undefined && properties[key] != this[key] )
                return false;
        return true;
    }

    WorldState.prototype.apply = function( properties ) {
        for( key of this.basic_keys )
            if( properties[key] !== undefined )
                this[ key ] = properties[ key ];
    }

    function Action() {}
    Action.prototype.init = function( pre, eff, cost ) {
        this.preconditions = pre;
        this.effects = eff;
        this.cost = cost;
    }

    Action.prototype.available = function( state ) {
        return state.fulfills( this.preconditions ) && 
            this.additionalPreconditions();
    }

    Action.prototype.apply = function( state ) {
        result = new WorldState( state );
        result.apply( this.effects );
        return result;
    }

    Action.prototype.complete = function( state ) {
        return state.fulfills( this.effects );
    }

    Action.prototype.additionalPreconditions = function() {
        return true;
    }

    function FireAction() {
        this.init( 
            new WorldState({ weaponCool: true, aligned: true }), 
            new WorldState({ weaponCool: false, targetDestroyed: true }),
            1.0 );
    }
    FireAction.prototype = new Action();
    FireAction.prototype.type = "fire";

    FireAction.prototype.activate = function( state ) {
        state.parent.alignTo( state.target );
        //state.parent.weapon.fire();
    }

    function AlignAction() {
        this.init( 
            new WorldState({ RCSFuel: true }),
            new WorldState({ aligned: true }),
            4.0 );
    }
    AlignAction.prototype = new Action();
    AlignAction.prototype.type = "align";

    AlignAction.prototype.activate = function( state ) {
        state.parent.alignTo( state.target );
    }


    function Goal() {}
    Goal.prototype.init = function( state ) {
        this.state = state;
    }

    function KillEnemyGoal() {
        this.init( new WorldState({ targetDestroyed: true }) );
    }
    KillEnemyGoal.prototype = new Goal();
    KillEnemyGoal.prototype.type = "kill_enemy";
        
    function AI( parent, PC ) {
        this.parent = parent;
        this.target = PC;

        this.goals = [new KillEnemyGoal(PC)];
        this.actions = [new FireAction(), new AlignAction()];

        this.current_action = null;
        this.plan = [];
    }

    AI.prototype.buildPlan = function( state ) {
        goal = this.goals[0].state;

        compare = function( s1, s2 ) {
            // Return opposite ordering to get lowest costs
            if( s1.cost < s2.cost ) return 1;
            if( s1.cost > s2.cost ) return -1;
            return 0;
        }

        queue = new buckets.PriorityQueue( compare );
        state.g = 0.0;
        state.cost = state.distance( goal );
        queue.add( state );

        while( !queue.isEmpty() ) {
            state = queue.dequeue();
            if( state.fulfills( goal ) )
                break;

            for( var i = 0; i < this.actions.length; ++i ) {
                action = this.actions[i];
                if( !action.available( state ) ) continue;

                new_state = action.apply( state );
                new_state.parent = state;
                new_state.action = action;

                // Should check if new_state already exists in queue
                new_state.g = state.g + action.cost;
                new_state.cost = new_state.g + new_state.distance( goal );
                queue.add( new_state );
            }
        }

        this.plan = [];
        while( state.parent.parent ) {
            this.plan.push( state.action );
            state = state.parent;
        }
        this.plan.reverse();

        this.current_action = this.plan[0];
        this.place = 0;
    }

    AI.prototype.update = function() {
        if( !this.parent.loaded ) return;

        state = new WorldState();
        state.build( this.parent, this.target );
        if( !this.current_action ) {
            this.buildPlan( state );
        }

        this.current_action.activate( state );
        if( this.current_action.complete( state ) )
            this.current_action = this.plan[ ++this.place ];
    }

    return { AI: AI };
});
