import tensorflow as tf


def categorical_focal_crossentropy(
        y_true,
        y_pred,
        alpha=0.25,
        gamma=2.0,
        from_logits=False,
        axis=-1,
):
    if from_logits:
        y_pred = tf.math.softmax(y_pred, axis=axis)

    # Adjust the predictions so that the probability of
    # each class for every sample adds up to 1
    # This is needed to ensure that the cross entropy is
    # computed correctly.
    output = y_pred / tf.math.reduce_sum(y_pred, axis=axis, keepdims=True)
    output = tf.clip_by_value(output, tf.keras.backend.epsilon(), 1.0 - tf.keras.backend.epsilon())

    # Calculate cross entropy
    cce = -y_true * tf.math.log(output)

    # Calculate factors
    modulating_factor = tf.math.pow(1.0 - output, gamma)
    weighting_factor = tf.math.multiply(modulating_factor, alpha)

    # Apply weighting factor
    focal_cce = tf.math.multiply(weighting_factor, cce)
    focal_cce = tf.math.reduce_sum(focal_cce, axis=axis)
    return focal_cce