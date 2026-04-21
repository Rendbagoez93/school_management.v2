# Behavioral Patterns

Patterns concerned with algorithms and assignment of responsibilities between objects.

---

## Observer

**Intent:** Define one-to-many dependency, notify dependents automatically  
**Use when:** State change needs to update multiple dependent objects

### AI Pseudocode
```
INTERFACE Observer {
  FN update(state: any): void
}

CLASS Subject {
  -observers: List<Observer>
  -state: any
  
  METHOD attach(o: Observer): void {
    this.observers.add(o)
  }
  
  METHOD detach(o: Observer): void {
    this.observers.remove(o)
  }
  
  METHOD notify(): void {
    FOR o IN this.observers {
      o.update(this.state)
    }
  }
  
  METHOD setState(s: any): void {
    this.state = s
    this.notify()
  }
}
```

### TypeScript
```typescript
interface Observer {
  update(state: any): void;
}

class Subject {
  private observers: Observer[] = [];
  private state: any;
  
  attach(observer: Observer): void {
    this.observers.push(observer);
  }
  
  detach(observer: Observer): void {
    const index = this.observers.indexOf(observer);
    if (index !== -1) {
      this.observers.splice(index, 1);
    }
  }
  
  notify(): void {
    for (const observer of this.observers) {
      observer.update(this.state);
    }
  }
  
  setState(state: any): void {
    this.state = state;
    this.notify();
  }
}
```

### Rust
```rust
trait Observer {
    fn update(&self, state: &str);
}

struct Subject<'a> {
    observers: Vec<Box<dyn Observer + 'a>>,
    state: String,
}

impl<'a> Subject<'a> {
    fn new() -> Self {
        Subject {
            observers: Vec::new(),
            state: String::new(),
        }
    }
    
    fn attach(&mut self, observer: Box<dyn Observer + 'a>) {
        self.observers.push(observer);
    }
    
    fn notify(&self) {
        for observer in &self.observers {
            observer.update(&self.state);
        }
    }
    
    fn set_state(&mut self, state: &str) {
        self.state = state.to_string();
        self.notify();
    }
}
```

### Java
```java
import java.util.ArrayList;
import java.util.List;

interface Observer {
    void update(String state);
}

class Subject {
    private List<Observer> observers = new ArrayList<>();
    private String state;
    
    void attach(Observer observer) {
        observers.add(observer);
    }
    
    void detach(Observer observer) {
        observers.remove(observer);
    }
    
    void notifyObservers() {
        for (Observer observer : observers) {
            observer.update(state);
        }
    }
    
    void setState(String state) {
        this.state = state;
        notifyObservers();
    }
}
```

### Python
```python
from abc import ABC, abstractmethod
from typing import List

class Observer(ABC):
    @abstractmethod
    def update(self, state: str) -> None: pass

class Subject:
    def __init__(self):
        self._observers: List[Observer] = []
        self._state: str = ""
    
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
    
    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self._state)
    
    def set_state(self, state: str) -> None:
        self._state = state
        self.notify()
```

**When to use:**
- Maintain consistency across related objects
- Notify without tight coupling
- Support broadcast communication

**Common mistakes:**
- Circular updates
- Forgetting to detach observers (memory leaks)
- Over-triggering notifications

**Modern alternatives:**
- Event buses / pub-sub
- Reactive programming (Rx)
- Signals (Solid, Preact)

---

## Strategy

**Intent:** Define family of algorithms, encapsulate each one, make them interchangeable  
**Use when:** Many related classes differ only in behavior

### AI Pseudocode
```
INTERFACE Strategy {
  FN execute(data: List): List
}

CLASS Context {
  -strategy: Strategy
  
  METHOD setStrategy(s: Strategy): void {
    this.strategy = s
  }
  
  METHOD executeStrategy(data: List): List {
    RETURN this.strategy.execute(data)
  }
}

CLASS StrategyA IMPLEMENTS Strategy {
  FN execute(data: List): List {
    RETURN sort_ascending(data)
  }
}

CLASS StrategyB IMPLEMENTS Strategy {
  FN execute(data: List): List {
    RETURN sort_descending(data)
  }
}
```

### TypeScript
```typescript
interface Strategy {
  execute(data: number[]): number[];
}

class Context {
  private strategy: Strategy;
  
  setStrategy(strategy: Strategy): void {
    this.strategy = strategy;
  }
  
  executeStrategy(data: number[]): number[] {
    return this.strategy.execute(data);
  }
}

class StrategyA implements Strategy {
  execute(data: number[]): number[] {
    return [...data].sort((a, b) => a - b);
  }
}

class StrategyB implements Strategy {
  execute(data: number[]): number[] {
    return [...data].sort((a, b) => b - a);
  }
}
```

### Rust
```rust
trait Strategy {
    fn execute(&self, data: &mut [i32]);
}

struct Context<T: Strategy> {
    strategy: T,
}

impl<T: Strategy> Context<T> {
    fn new(strategy: T) -> Self {
        Context { strategy }
    }
    
    fn set_strategy<U: Strategy>(self, strategy: U) -> Context<U> {
        Context { strategy }
    }
    
    fn execute_strategy(&self, data: &mut [i32]) {
        self.strategy.execute(data);
    }
}

struct StrategyA;
impl Strategy for StrategyA {
    fn execute(&self, data: &mut [i32]) {
        data.sort();
    }
}
```

### Java
```java
interface Strategy {
    int[] execute(int[] data);
}

class Context {
    private Strategy strategy;
    
    void setStrategy(Strategy strategy) {
        this.strategy = strategy;
    }
    
    int[] executeStrategy(int[] data) {
        return strategy.execute(data);
    }
}

class StrategyA implements Strategy {
    public int[] execute(int[] data) {
        return java.util.Arrays.stream(data).sorted().toArray();
    }
}

class StrategyB implements Strategy {
    public int[] execute(int[] data) {
        return java.util.Arrays.stream(data)
            .boxed()
            .sorted(java.util.Collections.reverseOrder())
            .mapToInt(Integer::intValue)
            .toArray();
    }
}
```

### Python
```python
from abc import ABC, abstractmethod
from typing import List

class Strategy(ABC):
    @abstractmethod
    def execute(self, data: List[int]) -> List[int]: pass

class Context:
    def __init__(self):
        self._strategy: Strategy | None = None
    
    def set_strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy
    
    def execute_strategy(self, data: List[int]) -> List[int]:
        if self._strategy:
            return self._strategy.execute(data)
        return data

class StrategyA(Strategy):
    def execute(self, data: List[int]) -> List[int]:
        return sorted(data)

class StrategyB(Strategy):
    def execute(self, data: List[int]) -> List[int]:
        return sorted(data, reverse=True)
```

**When to use:**
- Multiple variants of algorithm
- Avoid exposing complex algorithm-specific data structures
- Class defines many behaviors using multiple conditional statements

**Strategy vs State:**
- Strategy = algorithm choice from client
- State = behavior changes based on internal state transitions

---

## Command

**Intent:** Encapsulate request as object, parameterize clients with different requests  
**Use when:** Need to parameterize objects by action to perform

### AI Pseudocode
```
INTERFACE Command {
  FN execute(): void
  FN undo(): void
}

CLASS Receiver {
  FN action(arg: str): void {
    // Perform action
  }
  
  FN getState(): str { RETURN current_state }
  FN setState(s: str): void { current_state = s }
}

CLASS ConcreteCommand IMPLEMENTS Command {
  -receiver: Receiver
  -arg: str
  -prevState: str
  
  CONSTRUCTOR(r: Receiver, a: str) {
    this.receiver = r
    this.arg = a
  }
  
  FN execute(): void {
    this.prevState = this.receiver.getState()
    this.receiver.action(this.arg)
  }
  
  FN undo(): void {
    this.receiver.setState(this.prevState)
  }
}
```

### TypeScript
```typescript
interface Command {
  execute(): void;
  undo(): void;
}

class Receiver {
  private state = "";
  
  action(arg: string): void {
    this.state = arg;
  }
  
  getState(): string { return this.state; }
  setState(state: string): void { this.state = state; }
}

class ConcreteCommand implements Command {
  private prevState: string = "";
  
  constructor(
    private receiver: Receiver,
    private arg: string
  ) {}
  
  execute(): void {
    this.prevState = this.receiver.getState();
    this.receiver.action(this.arg);
  }
  
  undo(): void {
    this.receiver.setState(this.prevState);
  }
}
```

### Rust
```rust
trait Command {
    fn execute(&mut self);
    fn undo(&mut self);
}

struct Receiver {
    state: String,
}

impl Receiver {
    fn action(&mut self, arg: &str) {
        self.state = arg.to_string();
    }
}

struct ConcreteCommand<'a> {
    receiver: &'a mut Receiver,
    arg: String,
    prev_state: String,
}

impl<'a> Command for ConcreteCommand<'a> {
    fn execute(&mut self) {
        self.prev_state = self.receiver.state.clone();
        self.receiver.action(&self.arg);
    }
    
    fn undo(&mut self) {
        self.receiver.state = self.prev_state.clone();
    }
}
```

### Java
```java
interface Command {
    void execute();
    void undo();
}

class Receiver {
    private String state = "";
    
    void action(String arg) { state = arg; }
    String getState() { return state; }
    void setState(String state) { this.state = state; }
}

class ConcreteCommand implements Command {
    private Receiver receiver;
    private String arg;
    private String prevState;
    
    ConcreteCommand(Receiver receiver, String arg) {
        this.receiver = receiver;
        this.arg = arg;
    }
    
    public void execute() {
        prevState = receiver.getState();
        receiver.action(arg);
    }
    
    public void undo() {
        receiver.setState(prevState);
    }
}
```

### Python
```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: pass
    
    @abstractmethod
    def undo(self) -> None: pass

class Receiver:
    def __init__(self):
        self._state = ""
    
    def action(self, arg: str) -> None:
        self._state = arg
    
    def get_state(self) -> str:
        return self._state
    
    def set_state(self, state: str) -> None:
        self._state = state

class ConcreteCommand(Command):
    def __init__(self, receiver: Receiver, arg: str):
        self._receiver = receiver
        self._arg = arg
        self._prev_state = ""
    
    def execute(self) -> None:
        self._prev_state = self._receiver.get_state()
        self._receiver.action(self._arg)
    
    def undo(self) -> None:
        self._receiver.set_state(self._prev_state)
```

**Use case examples:**
- Undo/redo functionality
- Job queues
- Macro recording
- Transaction systems

---

## State

**Intent:** Allow object to alter behavior when internal state changes  
**Use when:** Object's behavior depends on its state, and changes at runtime

### AI Pseudocode
```
CLASS Context {
  -state: State
  
  METHOD setState(s: State): void {
    this.state = s
  }
  
  METHOD request(): void {
    this.state.handle(this)
  }
}

INTERFACE State {
  FN handle(ctx: Context): void
}

CLASS StateA IMPLEMENTS State {
  FN handle(ctx: Context): void {
    ctx.setState(NEW StateB())
  }
}

CLASS StateB IMPLEMENTS State {
  FN handle(ctx: Context): void {
    ctx.setState(NEW StateA())
  }
}
```

### TypeScript
```typescript
interface State {
  handle(context: Context): void;
}

class Context {
  private state: State;
  
  setState(state: State): void {
    this.state = state;
  }
  
  request(): void {
    this.state.handle(this);
  }
}

class StateA implements State {
  handle(context: Context): void {
    context.setState(new StateB());
  }
}

class StateB implements State {
  handle(context: Context): void {
    context.setState(new StateA());
  }
}
```

### Rust
```rust
trait State {
    fn handle(&self, context: &mut Context);
}

struct Context {
    state: Box<dyn State>,
}

impl Context {
    fn set_state(&mut self, state: Box<dyn State>) {
        self.state = state;
    }
    
    fn request(&mut self) {
        let new_state = self.state.handle_and_return(self);
        self.state = new_state;
    }
}

struct StateA;
impl State for StateA {
    fn handle(&self, context: &mut Context) {
        context.set_state(Box::new(StateB));
    }
}

struct StateB;
impl State for StateB {
    fn handle(&self, context: &mut Context) {
        context.set_state(Box::new(StateA));
    }
}
```

### Java
```java
interface State {
    void handle(Context context);
}

class Context {
    private State state;
    
    void setState(State state) {
        this.state = state;
    }
    
    void request() {
        state.handle(this);
    }
}

class StateA implements State {
    public void handle(Context context) {
        context.setState(new StateB());
    }
}

class StateB implements State {
    public void handle(Context context) {
        context.setState(new StateA());
    }
}
```

### Python
```python
from abc import ABC, abstractmethod

class State(ABC):
    @abstractmethod
    def handle(self, context: 'Context') -> None: pass

class Context:
    def __init__(self):
        self._state: State | None = None
    
    def set_state(self, state: State) -> None:
        self._state = state
    
    def request(self) -> None:
        if self._state:
            self._state.handle(self)

class StateA(State):
    def handle(self, context: Context) -> None:
        context.set_state(StateB())

class StateB(State):
    def handle(self, context: Context) -> None:
        context.set_state(StateA())
```

**When to use:**
- Operations have large, multipart conditional statements
- State-specific behavior not easily represented with data

**State vs Strategy:**
- State: Context delegates to state based on its own state
- Strategy: Client chooses strategy, passes to context

---

## Iterator

**Intent:** Provide way to access elements sequentially without exposing representation  
**Use when:**
- Custom data structures
- Different traversal algorithms needed
- Hide complex traversal logic

### TypeScript
```typescript
interface Iterator<T> {
  next(): T | null;
  hasNext(): boolean;
}

class ConcreteIterator<T> implements Iterator<T> {
  private index = 0;
  
  constructor(private collection: T[]) {}
  
  next(): T | null {
    if (this.hasNext()) {
      return this.collection[this.index++];
    }
    return null;
  }
  
  hasNext(): boolean {
    return this.index < this.collection.length;
  }
}
```

### Rust
```rust
struct MyCollection<T> {
    items: Vec<T>,
}

impl<T> IntoIterator for MyCollection<T> {
    type Item = T;
    type IntoIter = std::vec::IntoIter<T>;
    
    fn into_iter(self) -> Self::IntoIter {
        self.items.into_iter()
    }
}
```

### Java
```java
interface Iterator<T> {
    boolean hasNext();
    T next();
}

class ConcreteIterator<T> implements Iterator<T> {
    private List<T> collection;
    private int index = 0;
    
    ConcreteIterator(List<T> collection) {
        this.collection = collection;
    }
    
    public boolean hasNext() {
        return index < collection.size();
    }
    
    public T next() {
        return collection.get(index++);
    }
}
```

### Python
```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Iterator:
    def __init__(self, collection: List[T]):
        self._collection = collection
        self._index = 0
    
    def __next__(self) -> T:
        if self._index < len(self._collection):
            result = self._collection[self._index]
            self._index += 1
            return result
        raise StopIteration
    
    def __iter__(self):
        return self

# Python usually uses built-in iter()
```

---

## Chain of Responsibility

**Intent:** Avoid coupling sender of request to receiver by giving multiple objects chance to handle request  
**Use when:**
- Multiple handlers for request
- Handler not known in advance
- Set of handlers should change dynamically

### TypeScript
```typescript
abstract class Handler {
  protected nextHandler?: Handler;
  
  setNext(handler: Handler): Handler {
    this.nextHandler = handler;
    return handler;
  }
  
  handle(request: string): string | null {
    if (this.nextHandler) {
      return this.nextHandler.handle(request);
    }
    return null;
  }
}

class ConcreteHandler1 extends Handler {
  handle(request: string): string | null {
    if (request === "type1") {
      return "Handler1 handled it";
    }
    return super.handle(request);
  }
}
```

---

## Template Method

**Intent:** Define skeleton of algorithm, deferring steps to subclasses  
**Use when:**
- Implement invariant parts once
- Common behavior with customizable parts

### TypeScript
```typescript
abstract class AbstractClass {
  templateMethod(): void {
    this.step1();
    this.requiredStep();
    this.step2();
    this.hook();
  }
  
  private step1(): void {
    console.log("AbstractClass: Step1");
  }
  
  private step2(): void {
    console.log("AbstractClass: Step2");
  }
  
  abstract requiredStep(): void;
  
  protected hook(): void {} // optional override
}

class ConcreteClass extends AbstractClass {
  requiredStep(): void {
    console.log("ConcreteClass: RequiredStep");
  }
  
  protected hook(): void {
    console.log("ConcreteClass: Hook");
  }
}
```

### Rust
```rust
trait Template {
    fn template_method(&self) {
        self.step1();
        self.required_step();
        self.step2();
        self.hook();
    }
    
    fn step1(&self) { println!("Step1"); }
    fn step2(&self) { println!("Step2"); }
    fn required_step(&self);
    fn hook(&self) {} // default empty
}

struct Concrete;
impl Template for Concrete {
    fn required_step(&self) {
        println!("RequiredStep");
    }
}
```

### Java
```java
abstract class AbstractClass {
    final void templateMethod() {
        step1();
        requiredStep();
        step2();
        hook();
    }
    
    private void step1() { System.out.println("Step1"); }
    private void step2() { System.out.println("Step2"); }
    
    abstract void requiredStep();
    void hook() {} // optional
}

class ConcreteClass extends AbstractClass {
    void requiredStep() {
        System.out.println("RequiredStep");
    }
    
    void hook() {
        System.out.println("Hook");
    }
}
```

### Python
```python
from abc import ABC, abstractmethod

class AbstractClass(ABC):
    def template_method(self) -> None:
        self._step1()
        self._required_step()
        self._step2()
        self._hook()
    
    def _step1(self) -> None:
        print("Step1")
    
    def _step2(self) -> None:
        print("Step2")
    
    @abstractmethod
    def _required_step(self) -> None: pass
    
    def _hook(self) -> None: pass  # optional

class ConcreteClass(AbstractClass):
    def _required_step(self) -> None:
        print("RequiredStep")
    
    def _hook(self) -> None:
        print("Hook")
```