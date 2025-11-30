"""
Service Commands
================

Commands for service roles:
- Task assignment
- Uniform management
- Performances
"""

from evennia import Command, CmdSet

from .service import (
    ServiceRole, TaskType, PerformanceType,
    ServiceSystem, ServiceTask, ALL_UNIFORMS
)


class CmdAssignTask(Command):
    """
    Assign a task to a servant.
    
    Usage:
      task <servant> <type> <description>
    
    Types: cleaning, serving, cooking, attending, 
           errands, performance, display, sexual
    
    Examples:
      task Luna cleaning Polish the floors
      task Rex serving Bring refreshments to guests
    """
    
    key = "task"
    aliases = ["assign", "order"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Usage: task <servant> <type> <description>")
            return
        
        args = self.args.strip().split(None, 2)
        if len(args) < 3:
            self.caller.msg("Usage: task <servant> <type> <description>")
            return
        
        target_name, task_type_str, description = args
        
        target = self.caller.search(target_name)
        if not target:
            return
        
        # Parse task type
        try:
            task_type = TaskType(task_type_str.lower())
        except ValueError:
            valid = ", ".join([t.value for t in TaskType])
            self.caller.msg(f"Invalid task type. Valid: {valid}")
            return
        
        # Create and assign task
        task = ServiceSystem.assign_task(
            self.caller, target, task_type, description
        )
        
        if hasattr(target, 'add_task'):
            target.add_task(task)
        
        self.caller.msg(f"Assigned {task_type.value} task to {target.key}: {description}")
        target.msg(f"{self.caller.key} has assigned you a task: {description}")


class CmdTasks(Command):
    """
    View your assigned tasks.
    
    Usage:
      tasks
      tasks start <task_id>
      tasks complete <task_id>
    """
    
    key = "tasks"
    aliases = ["mytasks"]
    locks = "cmd:all()"
    
    def func(self):
        if not hasattr(self.caller, 'current_tasks'):
            self.caller.msg("You have no tasks.")
            return
        
        args = self.args.strip().split() if self.args else []
        
        if not args:
            # View tasks
            tasks = self.caller.current_tasks
            
            if not tasks:
                self.caller.msg("You have no assigned tasks.")
                return
            
            lines = ["=== Your Tasks ==="]
            for task in tasks:
                status = task.status.value
                time_str = f"{task.time_remaining}m" if task.time_remaining > 0 else "OVERDUE"
                lines.append(f"  [{task.task_id}] {task.description}")
                lines.append(f"      Type: {task.task_type.value}, Status: {status}, Time: {time_str}")
            
            self.caller.msg("\n".join(lines))
            return
        
        cmd = args[0].lower()
        
        if len(args) < 2:
            self.caller.msg("Specify a task ID.")
            return
        
        task_id = args[1]
        task = self.caller.get_task(task_id)
        
        if not task:
            self.caller.msg(f"Task {task_id} not found.")
            return
        
        if cmd == "start":
            message = task.start()
            self.caller.update_task(task)
            self.caller.msg(message)
        
        elif cmd == "complete":
            success, message = task.complete()
            self.caller.update_task(task)
            self.caller.msg(message)
            
            # Notify assigner
            if task.assigner_dbref:
                assigner = self.caller.search(task.assigner_dbref)
                if assigner:
                    assigner.msg(f"{self.caller.key} has completed a task: {task.description}")


class CmdUniform(Command):
    """
    Put on or view service uniforms.
    
    Usage:
      uniform                    - View current uniform
      uniform list               - List available uniforms
      uniform <name>             - Put on a uniform
      uniform remove             - Remove uniform
    """
    
    key = "uniform"
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            # View current
            if not hasattr(self.caller, 'current_uniform'):
                self.caller.msg("You're not wearing a uniform.")
                return
            
            uniform_key = self.caller.current_uniform
            if not uniform_key:
                self.caller.msg("You're not wearing a uniform.")
                return
            
            uniform = ALL_UNIFORMS.get(uniform_key)
            if uniform:
                self.caller.msg(f"Wearing: {uniform.name}\n{uniform.description}")
            return
        
        if args == "list":
            lines = ["=== Available Uniforms ==="]
            for key, uniform in ALL_UNIFORMS.items():
                lines.append(f"  {key}: {uniform.name}")
                lines.append(f"      {uniform.description}")
            self.caller.msg("\n".join(lines))
            return
        
        if args == "remove":
            if hasattr(self.caller, 'current_uniform'):
                self.caller.current_uniform = None
            self.caller.msg("You remove your uniform.")
            return
        
        # Put on uniform
        if args not in ALL_UNIFORMS:
            self.caller.msg(f"Unknown uniform: {args}")
            return
        
        uniform = ALL_UNIFORMS[args]
        self.caller.current_uniform = args
        self.caller.msg(f"You put on the {uniform.name}.")
        self.caller.location.msg_contents(
            f"{self.caller.key} puts on a {uniform.name}.",
            exclude=[self.caller]
        )


class CmdPerform(Command):
    """
    Start a performance.
    
    Usage:
      perform <type>
      perform continue
      perform stop
    
    Types: dance, strip, pose, display, entertain, pleasure
    """
    
    key = "perform"
    aliases = ["performance"]
    locks = "cmd:all()"
    
    def func(self):
        args = self.args.strip().lower() if self.args else ""
        
        if not args:
            # Show current performance
            if hasattr(self.caller, 'current_performance') and self.caller.current_performance:
                perf = self.caller.current_performance
                self.caller.msg(f"Performing: {perf.performance_type.value}, Stage {perf.stage}/{perf.max_stages}")
            else:
                self.caller.msg("Not currently performing. Use 'perform <type>' to start.")
            return
        
        if args == "continue":
            if not hasattr(self.caller, 'current_performance') or not self.caller.current_performance:
                self.caller.msg("You're not performing.")
                return
            
            perf = self.caller.current_performance
            finished, message = perf.advance_stage()
            
            self.caller.msg(message)
            self.caller.location.msg_contents(message, exclude=[self.caller])
            
            if finished:
                self.caller.current_performance = None
            else:
                self.caller.current_performance = perf
            return
        
        if args == "stop":
            if hasattr(self.caller, 'current_performance'):
                self.caller.current_performance = None
            self.caller.msg("You stop performing.")
            return
        
        # Start new performance
        try:
            perf_type = PerformanceType(args)
        except ValueError:
            valid = ", ".join([p.value for p in PerformanceType])
            self.caller.msg(f"Invalid performance type. Valid: {valid}")
            return
        
        perf = ServiceSystem.start_performance(
            self.caller, perf_type, self.caller.location
        )
        
        message = perf.start()
        self.caller.current_performance = perf
        
        self.caller.msg(message)
        self.caller.location.msg_contents(message, exclude=[self.caller])


class CmdTip(Command):
    """
    Tip a performer.
    
    Usage:
      tip <performer> <amount>
    """
    
    key = "tip"
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Tip who?")
            return
        
        args = self.args.strip().split()
        if len(args) < 2:
            self.caller.msg("Usage: tip <performer> <amount>")
            return
        
        target_name = args[0]
        try:
            amount = int(args[1])
        except ValueError:
            self.caller.msg("Amount must be a number.")
            return
        
        target = self.caller.search(target_name)
        if not target:
            return
        
        if not hasattr(target, 'current_performance') or not target.current_performance:
            self.caller.msg(f"{target.key} is not performing.")
            return
        
        perf = target.current_performance
        message = perf.add_tip(amount, self.caller.key)
        target.current_performance = perf
        
        self.caller.msg(f"You tip {target.key} {amount} coins.")
        target.msg(message)


class ServiceCmdSet(CmdSet):
    """Commands for service roles."""
    
    key = "ServiceCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdAssignTask())
        self.add(CmdTasks())
        self.add(CmdUniform())
        self.add(CmdPerform())
        self.add(CmdTip())
