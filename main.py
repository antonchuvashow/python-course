import asyncio
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


class CalculationRequest(BaseModel):
    numbers: list[float]
    delays: list[float]


class CalculationResult(BaseModel):
    number: float
    square: float
    delay: float
    time: float


class CalculationResponse(BaseModel):
    results: list[CalculationResult]
    total_time: float
    parallel_faster_than_sequential: bool


async def calculate_square(number: float, delay: float) -> CalculationResult:
    start_time = time.perf_counter()
    await asyncio.sleep(delay)

    return CalculationResult(
        number=number,
        square=number**2,
        delay=delay,
        time=round(time.perf_counter() - start_time, 2),
    )


@app.post("/calculate/", response_model=CalculationResponse)
async def calculate(data: CalculationRequest) -> CalculationResponse:
    if len(data.numbers) != len(data.delays):
        raise HTTPException(
            status_code=400,
            detail="Количество чисел и задержек должно совпадать",
        )
    if any(delay < 0 for delay in data.delays):
        raise HTTPException(
            status_code=400,
            detail="Задержки не могут быть отрицательными",
        )

    start_time = time.perf_counter()
    tasks = [
        calculate_square(number, delay)
        for number, delay in zip(data.numbers, data.delays)
    ]
    results = await asyncio.gather(*tasks)
    total_time = round(time.perf_counter() - start_time, 2)

    return CalculationResponse(
        results=results,
        total_time=total_time,
        parallel_faster_than_sequential=total_time < sum(data.delays),
    )
