// 최소 DB 어댑터 (픽스처용 스텁).
export const db = {
  async raw(_sql: string, _params?: unknown[]): Promise<any[]> {
    throw new Error("stub");
  },
  async transaction<T>(_fn: (tx: typeof db) => Promise<T>): Promise<T> {
    throw new Error("stub");
  },
};
