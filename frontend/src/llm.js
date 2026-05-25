import { CreateMLCEngine } from "@mlc-ai/web-llm";

const MODEL_ID = "SmolLM2-360M";

let engine = null;
let initPromise = null;

export function checkWebGPU() {
  if (!navigator.gpu) {
    return { supported: false, reason: "WebGPU is not supported in this browser. Please use Chrome 113+ or Edge 113+." };
  }
  return { supported: true };
}

export async function initEngine(onProgress) {
  if (engine) return engine;

  // Prevent concurrent initialization
  if (initPromise) return initPromise;

  initPromise = (async () => {
    try {
      const gpuStatus = checkWebGPU();
      if (!gpuStatus.supported) {
        throw new Error(gpuStatus.reason);
      }

      engine = await CreateMLCEngine(MODEL_ID, {
        initProgressCallback: (report) => {
          if (onProgress) onProgress(report);
        },
      });
      return engine;
    } catch (err) {
      engine = null;
      initPromise = null;
      throw err;
    }
  })();

  return initPromise;
}

export function isEngineReady() {
  return engine !== null;
}

export async function chat(messages, options = {}) {
  if (!engine) throw new Error("Engine not initialized. Please wait for the model to load or click 'Reload Model'.");

  const { maxTokens = 512, temperature = 0.3 } = options;

  const reply = await engine.chat.completions.create({
    messages,
    stream: true,
    max_tokens: maxTokens,
    temperature: temperature,
  });
  return reply;
}
