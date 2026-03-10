# Contributing to Mini Fail2Ban

Thank you for your interest in contributing to Mini Fail2Ban!

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)

### Suggesting Features

Feature requests are welcome! Please:
- Describe the feature clearly
- Explain the use case
- Consider backward compatibility

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Follow the coding standards (see below)
5. Test your changes
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Coding Standards

### Python Code

- Use English for all comments and docstrings
- Follow PEP 8 style guide
- Add docstrings to all functions/classes
- Keep functions focused and small
- Handle errors appropriately

### Example

```python
def ban_ip(self, ip):
    """
    Ban IP address using iptables
    
    Args:
        ip (str): IP address to ban
    """
    # Implementation here
```

### Shell Scripts

- Use English comments
- Follow bash best practices
- Add error handling (`set -e`)
- Make scripts portable

## Testing

Before submitting:
- Test on a clean system
- Verify all features work
- Check for memory leaks
- Test configuration hot-reload

## Questions?

Feel free to open an issue for any questions!
