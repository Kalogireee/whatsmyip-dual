FROM python:3.12-alpine3.24

RUN apk add --no-cache curl tzdata \
    && addgroup -S appgroup \
    && adduser -S appuser -G appgroup \
    && python -m pip uninstall -y pip setuptools wheel || true \
    && rm -rf \
        /usr/local/lib/python*/site-packages/pip* \
        /usr/local/lib/python*/site-packages/setuptools* \
        /usr/local/lib/python*/site-packages/wheel* \
        /usr/local/bin/pip* \
        /root/.cache

COPY app.py /app.py

RUN chown appuser:appgroup /app.py

USER appuser

EXPOSE 3464

CMD ["python", "/app.py"]
