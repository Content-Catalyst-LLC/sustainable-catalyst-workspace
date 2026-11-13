using JSON3
using LinearAlgebra
using Random
using Statistics

function fail(msg)
    error(msg)
end

function vecfloat(x; maxn=200000)
    x isa AbstractVector || fail("expected array")
    length(x) <= maxn || fail("array limit exceeded")
    return Float64[Float64(v) for v in x]
end

function matfloat(x; maxdim=256)
    x isa AbstractVector || fail("expected matrix")
    n = length(x); n > 0 || fail("matrix empty"); n <= maxdim || fail("matrix dimension exceeded")
    rows = [vecfloat(r; maxn=maxdim) for r in x]
    m = length(rows[1]); m > 0 || fail("matrix empty"); m <= maxdim || fail("matrix dimension exceeded")
    all(length(r)==m for r in rows) || fail("ragged matrix")
    return reduce(vcat, permutedims.(rows))
end

function rk4_linear(A, b, y0, dt, steps)
    y = copy(y0); states = Vector{Vector{Float64}}(); push!(states, copy(y))
    f(v) = A*v + b
    for _ in 1:steps
        k1=f(y); k2=f(y .+ 0.5*dt.*k1); k3=f(y .+ 0.5*dt.*k2); k4=f(y .+ dt.*k3)
        y .= y .+ (dt/6.0).*(k1 .+ 2 .* k2 .+ 2 .* k3 .+ k4)
        push!(states, copy(y))
    end
    return y, states
end

function polynomial_roots(coeff)
    c = vecfloat(coeff; maxn=257)
    length(c) >= 2 || fail("at least two coefficients required")
    abs(c[1]) > 0 || fail("leading coefficient must be nonzero")
    n=length(c)-1
    C=zeros(Float64,n,n)
    if n>1
        C[2:end,1:end-1] .= Matrix{Float64}(I,n-1,n-1)
    end
    C[:,end] .= -reverse(c[2:end] ./ c[1])
    vals=eigvals(C)
    vals=vals[canonical_order(vals)]
    return [[real(v),imag(v)] for v in vals]
end

# SC-MATH-01 M2: one canonical order for complex results (real part, then imaginary part; real parts within a
# relative 1e-9 tie), the same rule the Python compute path applies.
const ORDER_TIE = 1e-9
function canonical_order(vals)
    idx = sortperm(collect(1:length(vals)); by = i -> (real(vals[i]), imag(vals[i])))
    out = Int[]; i = 1
    while i <= length(idx)
        anchor = real(vals[idx[i]]); j = i + 1
        while j <= length(idx) && abs(real(vals[idx[j]]) - anchor) <= ORDER_TIE * max(1.0, abs(anchor)); j += 1; end
        append!(out, sort(idx[i:j-1]; by = k -> imag(vals[k])))
        i = j
    end
    return out
end
const ORDERING = Dict("method"=>"real-then-imaginary", "realTieRelative"=>ORDER_TIE)

# SC-MATH-01 M1: a bounded evaluator for the shared symbolic grammar (numbers, declared variables, + - * / ^,
# parentheses, sin cos tan exp log sqrt abs, pi, E). Hand-written recursive descent: nothing is parsed or
# evaluated as Julia code. Derivatives use forward-mode dual numbers, independent of SymPy's symbolic rules.
struct Dual
    v::Float64
    d::Float64
end
Dual(x::Real) = Dual(Float64(x), 0.0)
dv(x::Dual) = x.v
dv(x::Float64) = x
lift(x::Dual) = x
lift(x::Float64) = Dual(x)
Base.:+(a::Dual, b::Dual) = Dual(a.v + b.v, a.d + b.d)
Base.:-(a::Dual, b::Dual) = Dual(a.v - b.v, a.d - b.d)
Base.:-(a::Dual) = Dual(-a.v, -a.d)
Base.:*(a::Dual, b::Dual) = Dual(a.v * b.v, a.d * b.v + a.v * b.d)
Base.:/(a::Dual, b::Dual) = Dual(a.v / b.v, (a.d * b.v - a.v * b.d) / (b.v * b.v))
function dpow(a::Dual, b::Dual)
    if b.d == 0.0 && isinteger(b.v)
        n = b.v
        return Dual(a.v^n, n == 0 ? 0.0 : n * a.v^(n - 1) * a.d)
    end
    a.v > 0 || fail("non-real power at a declared point")
    val = a.v^b.v
    return Dual(val, val * (b.d * log(a.v) + b.v * a.d / a.v))
end
const UNARY = Dict(
    "sin"  => x -> Dual(sin(x.v), cos(x.v) * x.d),
    "cos"  => x -> Dual(cos(x.v), -sin(x.v) * x.d),
    "tan"  => x -> Dual(tan(x.v), x.d / cos(x.v)^2),
    "exp"  => x -> Dual(exp(x.v), exp(x.v) * x.d),
    "log"  => x -> (x.v > 0 || fail("log of a non-positive value"); Dual(log(x.v), x.d / x.v)),
    "sqrt" => x -> (x.v > 0 || fail("sqrt at a non-positive value"); Dual(sqrt(x.v), x.d / (2 * sqrt(x.v)))),
    "abs"  => x -> (x.v != 0 || x.d == 0 || fail("abs is not differentiable at zero"); Dual(abs(x.v), sign(x.v) * x.d)),
)
UNARY["Abs"] = UNARY["abs"]
const CONSTANTS = Dict("pi" => Float64(pi), "E" => Float64(MathConstants.e))

function tokenize(src::String)
    length(src) <= 4000 || fail("expression limit exceeded")
    occursin(r"^[A-Za-z0-9_+\-*/^()., \t]+$", src) || fail("expression contains disallowed characters")
    toks = Tuple{Symbol,String}[]; i = 1; n = lastindex(src)
    while i <= n
        c = src[i]
        if c == ' ' || c == '\t'; i += 1
        elseif isdigit(c) || (c == '.' && i < n && isdigit(src[i+1]))
            m = match(r"^(?:\d+\.?\d*|\.\d+)", src[i:end]); push!(toks, (:num, m.match)); i += length(m.match)
        elseif isletter(c) || c == '_'
            m = match(r"^[A-Za-z_][A-Za-z0-9_]*", src[i:end]); push!(toks, (:id, m.match)); i += length(m.match)
        elseif c == '*' && i < n && src[i+1] == '*'; push!(toks, (:op, "^")); i += 2
        elseif c in "+-*/^()"; push!(toks, (:op, string(c))); i += 1
        else fail("unsupported token")
        end
    end
    length(toks) <= 2000 || fail("expression complexity exceeded")
    return toks
end

mutable struct Parser
    toks::Vector{Tuple{Symbol,String}}
    pos::Int
    env::Dict{String,Dual}
    depth::Int
end
peektok(p::Parser) = p.pos <= length(p.toks) ? p.toks[p.pos] : (:end, "")
function expect!(p::Parser, s::String)
    peektok(p) == (:op, s) || fail("expected '$s'")
    p.pos += 1
end
function parse_expr(p::Parser)
    (p.depth += 1) <= 200 || fail("expression nesting exceeded")
    x = parse_term(p)
    while peektok(p) in ((:op, "+"), (:op, "-"))
        op = peektok(p)[2]; p.pos += 1; y = parse_term(p)
        x = op == "+" ? x + y : x - y
    end
    p.depth -= 1
    return x
end
function parse_term(p::Parser)
    x = parse_unary(p)
    while peektok(p) in ((:op, "*"), (:op, "/"))
        op = peektok(p)[2]; p.pos += 1; y = parse_unary(p)
        if op == "/"; y.v != 0 || fail("division by zero at a declared point"); end
        x = op == "*" ? x * y : x / y
    end
    return x
end
function parse_unary(p::Parser)
    if peektok(p) == (:op, "-"); p.pos += 1; return -parse_unary(p); end
    if peektok(p) == (:op, "+"); p.pos += 1; return parse_unary(p); end
    return parse_power(p)
end
function parse_power(p::Parser)
    base = parse_atom(p)
    if peektok(p) == (:op, "^")
        p.pos += 1
        return dpow(base, parse_unary(p))   # right-associative; binds tighter than unary minus on its left
    end
    return base
end
function parse_atom(p::Parser)
    kind, text = peektok(p)
    if kind == :num
        p.pos += 1; return Dual(parse(Float64, text))
    elseif kind == :id
        p.pos += 1
        if haskey(UNARY, text)
            expect!(p, "("); arg = parse_expr(p); expect!(p, ")")
            return UNARY[text](arg)
        elseif haskey(p.env, text); return p.env[text]
        elseif haskey(CONSTANTS, text); return Dual(CONSTANTS[text])
        end
        fail("unknown identifier")
    elseif (kind, text) == (:op, "(")
        p.pos += 1; x = parse_expr(p); expect!(p, ")"); return x
    end
    fail("unexpected token")
end

function expression_evaluate(payload)
    expr = String(payload["expression"]); variables = [String(v) for v in get(payload, "variables", [])]
    length(variables) <= 32 && all(v -> occursin(r"^[A-Za-z][A-Za-z0-9_]{0,31}$", v), variables) || fail("invalid variable list")
    action = String(get(payload, "action", "evaluate"))
    action in ("evaluate", "simplify", "differentiate") || fail("expression-evaluate supports evaluate, simplify and differentiate")
    wrt = action == "differentiate" ? String(get(payload, "variable", isempty(variables) ? "" : variables[1])) : ""
    action != "differentiate" || wrt in variables || fail("a declared variable is required")
    action != "differentiate" || Int(get(payload, "order", 1)) == 1 || fail("first derivatives only")
    points = payload["evaluateAt"]; points isa AbstractVector && 0 < length(points) <= 256 || fail("evaluateAt must list 1-256 points")
    toks = tokenize(expr); values = Float64[]
    for pt in points
        pt isa AbstractDict || fail("each point must be an object")
        ptd = Dict(String(k) => x for (k, x) in pairs(pt))
        Set(keys(ptd)) == Set(variables) || fail("each point must give every declared variable")
        env = Dict{String,Dual}()
        for v in variables
            x = ptd[v]; (x isa Real && !(x isa Bool) && isfinite(x)) || fail("point values must be finite numbers")
            env[v] = Dual(Float64(x), v == wrt ? 1.0 : 0.0)
        end
        p = Parser(toks, 1, env, 0); r = parse_expr(p); p.pos == length(toks) + 1 || fail("trailing tokens")
        val = action == "differentiate" ? r.d : r.v
        isfinite(val) || fail("result is not finite at a declared point")
        push!(values, val)
    end
    return Dict("kind"=>"expression-evaluation", "solver"=>(action == "differentiate" ? "forward-mode-dual" : "recursive-descent-float64"),
                "steps"=>length(values), "values"=>values,
                "identityCheck"=>Dict("method"=>"numerical-identity-at-declared-points", "proof"=>false, "action"=>action,
                                      "pointCount"=>length(values), "variable"=>wrt,
                                      "arithmetic"=>Dict("engine"=>"julia-float64", "reportedAs"=>"ieee754-binary64")))
end

# SC-MATH-01 M4: the numerical library identity this process actually loaded.
function numerical_libraries()
    libs = try
        [Dict("library"=>basename(l.libname), "interface"=>string(l.interface)) for l in BLAS.get_config().loaded_libs]
    catch
        Any[]
    end
    return Dict("source"=>"runtime-loaded", "julia"=>string(VERSION), "blasVendor"=>string(BLAS.vendor()),
                "blasLoaded"=>libs, "blasThreads"=>BLAS.get_num_threads(), "precision"=>"ieee754-binary64")
end

function execute(op, payload)
    if op == "workspace.polyglot.julia.ode-linear-rk4"
        A=matfloat(payload["A"]; maxdim=64); size(A,1)==size(A,2) || fail("A must be square")
        y0=vecfloat(payload["initialState"]; maxn=64); length(y0)==size(A,1) || fail("initial state dimension mismatch")
        b=haskey(payload,"forcing") ? vecfloat(payload["forcing"]; maxn=64) : zeros(length(y0)); length(b)==length(y0) || fail("forcing dimension mismatch")
        dt=Float64(get(payload,"dt",0.01)); steps=Int(get(payload,"steps",100)); 0 < dt <= 10 || fail("invalid dt"); 1 <= steps <= 20000 || fail("invalid steps")
        final,states=rk4_linear(A,b,y0,dt,steps)
        return Dict("kind"=>"linear-ode","solver"=>"rk4","steps"=>steps,"finalState"=>final,"metrics"=>Dict("dt"=>dt,"duration"=>dt*steps,"stateNorm"=>norm(final)),"trajectoryPreview"=>states[1:max(1,Int(ceil(length(states)/25))):end])
    elseif op == "workspace.polyglot.julia.lotka-volterra"
        alpha=Float64(payload["alpha"]); beta=Float64(payload["beta"]); delta=Float64(payload["delta"]); gamma=Float64(payload["gamma"]); dt=Float64(get(payload,"dt",0.01)); steps=Int(get(payload,"steps",1000)); 1 <= steps <= 20000 || fail("invalid steps")
        y=Float64[Float64(payload["initialPrey"]),Float64(payload["initialPredator"])]
        function f(v); x,z=v; return [alpha*x-beta*x*z, delta*x*z-gamma*z]; end
        for _ in 1:steps
            k1=f(y); k2=f(y .+ 0.5*dt.*k1); k3=f(y .+ 0.5*dt.*k2); k4=f(y .+ dt.*k3); y .= y .+ (dt/6).*(k1 .+ 2 .* k2 .+ 2 .* k3 .+ k4); if any(y .< 0); y .= max.(y, 0.0); end
        end
        return Dict("kind"=>"lotka-volterra","solver"=>"rk4","steps"=>steps,"finalState"=>Dict("prey"=>y[1],"predator"=>y[2]),"metrics"=>Dict("duration"=>dt*steps))
    elseif op == "workspace.polyglot.julia.monte-carlo-normal"
        mu=Float64(get(payload,"mean",0.0)); sigma=Float64(get(payload,"stdDev",1.0)); sigma>=0 || fail("stdDev must be nonnegative"); n=Int(get(payload,"samples",10000)); 100 <= n <= 500000 || fail("sample count out of bounds"); seed=Int(get(payload,"seed",42)); rng=MersenneTwister(seed); vals=mu .+ sigma.*randn(rng,n)
        return Dict("kind"=>"monte-carlo-normal","solver"=>"mersenne-twister","steps"=>n,"seed"=>seed,"metrics"=>Dict("sampleMean"=>mean(vals),"sampleStdDev"=>std(vals),"minimum"=>minimum(vals),"maximum"=>maximum(vals)))
    elseif op == "workspace.polyglot.julia.quadratic-optimize"
        Q=matfloat(payload["Q"]; maxdim=256); size(Q,1)==size(Q,2) || fail("Q must be square"); c=vecfloat(payload["c"]; maxn=256); length(c)==size(Q,1) || fail("dimension mismatch"); S=Symmetric(Q); isposdef(S) || fail("Q must be positive definite"); x=-(S\c); objective=0.5*dot(x,Q*x)+dot(c,x)
        return Dict("kind"=>"quadratic-optimization","solver"=>"cholesky-linear-solve","steps"=>1,"solution"=>x,"metrics"=>Dict("objective"=>objective,"gradientNorm"=>norm(Q*x+c)))
    elseif op == "workspace.polyglot.julia.eigen-analysis"
        A=matfloat(payload["matrix"]; maxdim=128); size(A,1)==size(A,2) || fail("matrix must be square"); vals=eigvals(A); vals=vals[canonical_order(vals)]; serial=[[real(v),imag(v)] for v in vals]
        return Dict("kind"=>"eigen-analysis","solver"=>"lapack-eigvals","steps"=>1,"eigenvalues"=>serial,"ordering"=>ORDERING,"metrics"=>Dict("spectralRadius"=>maximum(abs.(vals))))
    elseif op == "workspace.polyglot.julia.integrate-series"
        x=vecfloat(payload["x"]); y=vecfloat(payload["y"]); length(x)==length(y) || fail("x/y length mismatch"); length(x)>=2 || fail("at least two samples required"); all(diff(x).>0) || fail("x must be strictly increasing"); area=sum((x[2:end].-x[1:end-1]).*(y[2:end].+y[1:end-1])./2)
        return Dict("kind"=>"series-integration","solver"=>"trapezoidal","steps"=>length(x)-1,"integral"=>area,"metrics"=>Dict("samples"=>length(x)))
    elseif op == "workspace.polyglot.julia.polynomial-roots"
        roots=polynomial_roots(payload["coefficients"]); return Dict("kind"=>"polynomial-roots","solver"=>"companion-eigen","steps"=>1,"roots"=>roots,"ordering"=>ORDERING,"metrics"=>Dict("degree"=>length(roots)))
    elseif op == "workspace.polyglot.julia.parameter-sweep"
        A=matfloat(payload["A"]; maxdim=32); size(A,1)==size(A,2) || fail("A must be square"); y0=vecfloat(payload["initialState"]; maxn=32); values=vecfloat(payload["parameterValues"]; maxn=128); dt=Float64(get(payload,"dt",0.05)); steps=Int(get(payload,"steps",100)); 1 <= steps <= 5000 || fail("invalid steps"); results=[]
        for v in values; final,_=rk4_linear(v.*A,zeros(length(y0)),y0,dt,steps); push!(results,Dict("parameter"=>v,"finalState"=>final,"stateNorm"=>norm(final))); end
        return Dict("kind"=>"parameter-sweep","solver"=>"rk4","steps"=>steps,"results"=>results,"metrics"=>Dict("parameterCount"=>length(values),"duration"=>dt*steps))
    elseif op == "workspace.polyglot.julia.expression-evaluate"
        return expression_evaluate(payload)
    end
    fail("unsupported operation")
end

input_path=ARGS[1]; output_path=ARGS[2]
envelope=JSON3.read(read(input_path,String),Dict{String,Any})
op=String(envelope["operation"]); payload=Dict{String,Any}(envelope["payload"])
result=execute(op,payload)
out=Dict("ok"=>true,"schema"=>"sc-workspace-julia-runtime-result/1.0","runtime"=>"julia-simulation-numerical","operation"=>op,"boundedOperationsOnly"=>true,"arbitraryCodeExecution"=>false,"numericalLibraries"=>numerical_libraries(),"result"=>result)
write(output_path,JSON3.write(out))
