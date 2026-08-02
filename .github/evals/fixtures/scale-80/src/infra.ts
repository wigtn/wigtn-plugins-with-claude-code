// 인프라 스텁.
export const db = { async raw(_s: string, _p?: unknown[]): Promise<any> { throw new Error('stub'); } };
export const blob = { async remove(_k: string): Promise<void> { throw new Error('stub'); } };
export const pool = { async acquire(): Promise<any> { throw new Error('stub'); },
  async release(_c: unknown): Promise<void> {} };
export const search = { async index(_id: string, _b: unknown): Promise<void> {} };
