import shutil
from pathlib import Path

from tensorflow.keras.optimizers import Adam

from backend.enums import Stage
from backend.trainer.generic_trainer import GenericTrainer
from backend.utils import set_seed
from config.kitti_object_detection.data_generator_config import KittiDataGeneratorConfig
from config.kitti_object_detection.fcos.common_fcos_config import FCOSCommonConfig
from config.object_detectors.callbacks_config import CallbacksConfig
from config.object_detectors.fcos.fcos_loss_config import FCOSLossConfig
from config.object_detectors.fcos.fcos_model_config import FCOSModelConfig
from config.object_detectors.fcos.fcos_postprocessor_config import FCOSPostprocessingConfig
from config.object_detectors.fcos.fcos_preprocessor_config import FCOSPreprocessingConfig


class FCOSTrainerConfig:
    EXPERIMENT = FCOSCommonConfig.PREFIX / 'train'
    # EXPERIMENT = Path('outputs/test_train')

    EPOCHS = 20
    START_LR = 1e-4

    @staticmethod
    def build():
        return GenericTrainer(
            train_dataset=KittiDataGeneratorConfig.build(Stage.TRAIN),
            val_dataset=KittiDataGeneratorConfig.build(Stage.VAL),
            loss=FCOSLossConfig.build(
                image_size=KittiDataGeneratorConfig.INPUT_SHAPE[:2],
                strides_weights=FCOSCommonConfig.STRIDES_WEIGHTS
            ),
            optimizer=Adam(learning_rate=FCOSTrainerConfig.START_LR, clipnorm=1.),
            callbacks=CallbacksConfig.build(FCOSTrainerConfig.EXPERIMENT, KittiDataGeneratorConfig.LABELS),
            model=FCOSModelConfig.build(
                input_shape=KittiDataGeneratorConfig.INPUT_SHAPE,
                no_classes=len(KittiDataGeneratorConfig.LABELS),
                backbone_outputs=FCOSCommonConfig.BACKBONE_OUTPUTS,
            ),
            preprocessor=FCOSPreprocessingConfig.build(
                image_size=KittiDataGeneratorConfig.INPUT_SHAPE[:2],
                no_classes=len(KittiDataGeneratorConfig.LABELS),
                strides=FCOSCommonConfig.STRIDES,
                thresholds=FCOSCommonConfig.THRESHOLDS,
            ),
            postprocessor=FCOSPostprocessingConfig.build(
                image_size=KittiDataGeneratorConfig.INPUT_SHAPE[:2],
                max_boxes_per_image=KittiDataGeneratorConfig.MAX_BOXES_PER_IMAGE,
                batch_size=KittiDataGeneratorConfig.BATCH_SIZE
            ),
            epochs=FCOSTrainerConfig.EPOCHS
        )


if __name__ == '__main__':
    set_seed(0)
    shutil.copytree('config', FCOSTrainerConfig.EXPERIMENT / 'config', dirs_exist_ok=True)
    FCOSTrainerConfig.build().train()
