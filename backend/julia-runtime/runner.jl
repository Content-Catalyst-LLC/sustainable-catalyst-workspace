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
    return [[real(v),imag(v)] for v in vals]
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
        A=matfloat(payload["matrix"]; maxdim=128); size(A,1)==size(A,2) || fail("matrix must be square"); vals=eigvals(A); serial=[[real(v),imag(v)] for v in vals]
        return Dict("kind"=>"eigen-analysis","solver"=>"lapack-eigvals","steps"=>1,"eigenvalues"=>serial,"metrics"=>Dict("spectralRadius"=>maximum(abs.(vals))))
    elseif op == "workspace.polyglot.julia.integrate-series"
        x=vecfloat(payload["x"]); y=vecfloat(payload["y"]); length(x)==length(y) || fail("x/y length mismatch"); length(x)>=2 || fail("at least two samples required"); all(diff(x).>0) || fail("x must be strictly increasing"); area=sum((x[2:end].-x[1:end-1]).*(y[2:end].+y[1:end-1])./2)
        return Dict("kind"=>"series-integration","solver"=>"trapezoidal","steps"=>length(x)-1,"integral"=>area,"metrics"=>Dict("samples"=>length(x)))
    elseif op == "workspace.polyglot.julia.polynomial-roots"
        roots=polynomial_roots(payload["coefficients"]); return Dict("kind"=>"polynomial-roots","solver"=>"companion-eigen","steps"=>1,"roots"=>roots,"metrics"=>Dict("degree"=>length(roots)))
    elseif op == "workspace.polyglot.julia.parameter-sweep"
        A=matfloat(payload["A"]; maxdim=32); size(A,1)==size(A,2) || fail("A must be square"); y0=vecfloat(payload["initialState"]; maxn=32); values=vecfloat(payload["parameterValues"]; maxn=128); dt=Float64(get(payload,"dt",0.05)); steps=Int(get(payload,"steps",100)); 1 <= steps <= 5000 || fail("invalid steps"); results=[]
        for v in values; final,_=rk4_linear(v.*A,zeros(length(y0)),y0,dt,steps); push!(results,Dict("parameter"=>v,"finalState"=>final,"stateNorm"=>norm(final))); end
        return Dict("kind"=>"parameter-sweep","solver"=>"rk4","steps"=>steps,"results"=>results,"metrics"=>Dict("parameterCount"=>length(values),"duration"=>dt*steps))
    end
    fail("unsupported operation")
end

input_path=ARGS[1]; output_path=ARGS[2]
envelope=JSON3.read(read(input_path,String),Dict{String,Any})
op=String(envelope["operation"]); payload=Dict{String,Any}(envelope["payload"])
result=execute(op,payload)
out=Dict("ok"=>true,"schema"=>"sc-workspace-julia-runtime-result/1.0","runtime"=>"julia-simulation-numerical","operation"=>op,"boundedOperationsOnly"=>true,"arbitraryCodeExecution"=>false,"result"=>result)
write(output_path,JSON3.write(out))
