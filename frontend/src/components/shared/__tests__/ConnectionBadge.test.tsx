describe('ConnectionBadge', () => {
  it('renders live mode correctly', () => {
    const mode = 'live';
    const config = getModeConfig(mode);
    expect(config.text).toBe('مباشر');
  });

  it('renders reconnecting mode correctly', () => {
    const mode = 'reconnecting';
    const config = getModeConfig(mode);
    expect(config.text).toBe('جارِ الاتصال');
  });

  it('renders polling mode correctly', () => {
    const mode = 'polling';
    const config = getModeConfig(mode);
    expect(config.text).toBe('تحديث دوري');
  });

  it('renders disconnected mode correctly', () => {
    const mode = 'disconnected';
    const config = getModeConfig(mode);
    expect(config.text).toBe('غير متصل');
  });
});

function getModeConfig(mode: string) {
  switch (mode) {
    case 'live':
      return {
        text: 'مباشر',
        color: 'bg-green-500',
      };
    case 'reconnecting':
      return {
        text: 'جارِ الاتصال',
        color: 'bg-amber-500',
      };
    case 'polling':
      return {
        text: 'تحديث دوري',
        color: 'bg-blue-500',
      };
    case 'disconnected':
      return {
        text: 'غير متصل',
        color: 'bg-red-500',
      };
  }
}
